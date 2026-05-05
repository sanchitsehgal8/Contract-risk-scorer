"""FAISS vector store for document retrieval."""

import json
import os
import pickle
from typing import Any, Dict, List, Optional

import numpy as np
from faiss import IndexFlatL2, read_index, write_index
from langchain.schema import Document
from langchain.vectorstores import FAISS

from contract_risk_scorer.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH
from contract_risk_scorer.embeddings.embedder import Embedder


class FAISSStore:
    """FAISS-based vector store for contracts and precedents."""

    def __init__(self, embedder: Embedder):
        """
        Initialize FAISS store.

        Args:
            embedder: Embedder instance for creating embeddings
        """
        self.embedder = embedder
        self.vectorstore: Optional[FAISS] = None
        self.index_path = FAISS_INDEX_PATH
        self.metadata_path = FAISS_METADATA_PATH

    def build_index(self, documents: List[Document]) -> FAISS:
        """
        Build FAISS index from documents.

        Args:
            documents: List of LangChain Document objects with metadata

        Returns:
            FAISS vectorstore instance
        """
        if not documents:
            raise ValueError("No documents provided to build index")

        try:
            self.vectorstore = FAISS.from_documents(
                documents=documents, embedding=self.embedder.embeddings
            )
            return self.vectorstore
        except Exception as e:
            raise RuntimeError(f"Failed to build FAISS index: {str(e)}")

    def save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        if self.vectorstore is None:
            raise RuntimeError("No index to save. Build index first.")

        try:
            # Create directory if it doesn't exist
            os.makedirs(self.index_path, exist_ok=True)

            # Save FAISS index
            self.vectorstore.save_local(self.index_path)

        except Exception as e:
            raise RuntimeError(f"Failed to save FAISS index: {str(e)}")

    def load_index(self) -> FAISS:
        """
        Load FAISS index from disk.

        Returns:
            FAISS vectorstore instance
        """
        try:
            if not os.path.exists(self.index_path):
                raise FileNotFoundError(f"Index path not found: {self.index_path}")

            self.vectorstore = FAISS.load_local(
                self.index_path, embeddings=self.embedder.embeddings
            )
            return self.vectorstore

        except Exception as e:
            raise RuntimeError(f"Failed to load FAISS index: {str(e)}")

    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents with metadata
        """
        if self.vectorstore is None:
            raise RuntimeError("Index not loaded. Load or build index first.")

        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return results

        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")

    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        Search and return results with similarity scores.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            raise RuntimeError("Index not loaded. Load or build index first.")

        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results

        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing index.

        Args:
            documents: List of Document objects to add
        """
        if self.vectorstore is None:
            raise RuntimeError("Index not loaded. Load or build index first.")

        try:
            self.vectorstore.add_documents(documents)
        except Exception as e:
            raise RuntimeError(f"Failed to add documents: {str(e)}")

    def get_index_size(self) -> int:
        """
        Get number of vectors in index.

        Returns:
            Number of documents in index
        """
        if self.vectorstore is None:
            raise RuntimeError("Index not loaded")

        try:
            return self.vectorstore.index.ntotal
        except Exception as e:
            raise RuntimeError(f"Failed to get index size: {str(e)}")
