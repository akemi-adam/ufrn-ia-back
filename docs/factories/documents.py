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


class QdrantDocs(IDocumentsDB):
    '''
    Estabele a conexão com o banco de dados vetorial Qdrant.\n
    Realiza busca de dados, salva documentos e cria coleções.
    '''
    def __init__(self):
        self.client: QdrantClient = QdrantClient(url=get_env('QDRANT_URL')) # Configurar no .env
        self.encoder: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')

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
