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

