from abc import ABC, abstractmethod
from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
from uuid import uuid4

from utils.env import get_env


class IDocumentsDB(ABC):
    @abstractmethod
    def search(self, context: str, storage: str) -> str:
        pass
    
    @abstractmethod
    def save(self, documents: any, storage: str) -> None:
        pass

    @abstractmethod
    def create_storage(self, name: str) -> None:
        pass

    @abstractmethod
    def delete_storage(self, name: str) -> None:
        pass


class QdrantDocs(IDocumentsDB):
    '''
    Estabele a conexão com o banco de dados vetorial Qdrant.\n
    Realiza busca de dados, salva documentos e cria coleções.
    '''
    def __init__(self):
        self.client: QdrantClient = QdrantClient(url=get_env('QDRANT_URL')) # Configurar no .env
        self.encoder: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

    def document_to_str(self, document: dict):
        '''
        Transforma um dicionário (documento) em uma string
        '''
        return " ".join([f"{k}: {v};\n" for k, v in document.items() if v is not None])

    def search(self, context: str, storage: str) -> str:
        '''
        Procura e retorna registros similares ao contexto
        '''
        hits = self.client.query_points(
            collection_name=storage,
            query=self.encoder.encode(context).tolist(),
            limit=100,
        ).points
        return " \n".join([self.document_to_str(hit.payload) for hit in hits])
    
    def save(self, documents: any, storage: str) -> None:
        '''
        Salva uma lista de documentos numa coleção
        '''
        points = []
        for document in documents:
            text = self.document_to_str(document)
            vector = self.encoder.encode(text).tolist()
            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload=document
                )
            )
        self.client.upload_points(
            collection_name=storage,
            points=points
        )

    def format_storage_name(self, name: str) -> str:
        '''
        Formata o nome de um arquivo csv para ser o nome de uma coleção
        '''
        return name.replace('-', '_').replace('.csv', '')

    def create_storage(self, name) -> None:
        '''
        Cria uma nova coleção
        '''
        if name not in self.get_collections():
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=self.encoder.get_sentence_embedding_dimension(),
                    distance=models.Distance.COSINE,
                ),
            )
    
    def delete_storage(self, name: str) -> None:
        '''
        Remove uma coleção, se existir
        '''
        collections = self.get_collections()
        if name in collections:
            self.client.delete_collection(name)

    def get_collections(self):
        '''
        Retorna todas as coleções do banco
        '''
        return [collection.name for collection in self.client.get_collections().collections]


class DocumentsFactory(ABC):
    @abstractmethod
    def improve_prompt(self, user_prompt: str, memory: str) -> str:
        pass

    @abstractmethod
    def save(self, documents: any, storage: str) -> None:
        pass

    @abstractmethod
    def create_docs_db(self) -> IDocumentsDB:
        pass

    @abstractmethod
    def create_storage(self, name: str) -> None:
        pass

    @abstractmethod
    def delete_storage(self, name: str) -> None:
        pass


class QdrantFactory(DocumentsFactory):
    '''
    '''
    def __init__(self):
        super().__init__()
        self.docs_db: IDocumentsDB = self.create_docs_db()

    def improve_prompt(self, user_prompt: str, memory: str) -> str:
        context: str = 'Cursos de graduação:\n' + self.docs_db.search(user_prompt, 'cursos_de_graduacao')
        context += '\n\nDocentes' + self.docs_db.search(user_prompt, 'docentes') # Temporário
        # context += '\n\nTurmas' + self.docs_db.search(user_prompt, 'turmas_2022.1') # Temporário
        prompt = f'''
        Você é um assistente inteligente. Use as informações a seguir para responder à pergunta do usuário.

        Informações recuperadas (contexto):
        {context}

        Memória das últimas interações com o usuário:
        {memory}

        Pergunta do usuário:
        {user_prompt}

        Instruções:
        - Use apenas as informações fornecidas acima.
        - Se não souber a resposta, diga "Não tenho informações suficientes".
        - Seja conciso, claro e objetivo.
        - Evite inventar respostas.
        - Caso haja múltiplas fontes conflitantes, indique que a informação é baseada nas fontes disponíveis.

        Resposta:
        '''
        return prompt

    def save(self, documents: any, storage: str) -> None:
        self.docs_db.save(documents, self.docs_db.format_storage_name(storage))

    def create_storage(self, name: str) -> None:
        self.docs_db.create_storage(self.docs_db.format_storage_name(name))

    def create_docs_db(self) -> IDocumentsDB:
        return QdrantDocs()
    
    def delete_storage(self, name: str) -> None:
        self.docs_db.delete_storage(self.docs_db.format_storage_name(name))
