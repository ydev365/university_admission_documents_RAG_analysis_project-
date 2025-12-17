import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from app.config import get_settings

settings = get_settings()


class VectorDBService:
    _instance = None
    _client = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDBService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name="setuek_collection",
                metadata={"description": "세부능력특기사항 데이터"}
            )

    @property
    def collection(self):
        return self._collection

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None
    ):
        if embeddings:
            self._collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
        else:
            self._collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where:
            params["where"] = where

        return self._collection.query(**params)

    def get_collection_count(self) -> int:
        return self._collection.count()

    def delete_collection(self):
        self._client.delete_collection("setuek_collection")
        self._collection = self._client.get_or_create_collection(
            name="setuek_collection",
            metadata={"description": "세부능력특기사항 데이터"}
        )
