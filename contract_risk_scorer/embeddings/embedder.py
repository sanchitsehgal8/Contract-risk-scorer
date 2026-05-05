"""HuggingFace embeddings via LangChain."""

from typing import List

from langchain.embeddings.huggingface import HuggingFaceEmbeddings

from contract_risk_scorer.config import EMBEDDING_MODEL_NAME


class Embedder:
    """Wrapper for HuggingFace sentence-transformers embeddings."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        """
        Initialize embedder with HuggingFace model.

        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                embedding = self.embeddings.embed_query(text)
                embeddings.append(embedding)
            except Exception as e:
                raise RuntimeError(f"Failed to embed text: {str(e)}")

        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query text.

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        try:
            return self.embeddings.embed_query(query)
        except Exception as e:
            raise RuntimeError(f"Failed to embed query: {str(e)}")

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Embed multiple documents.

        Args:
            documents: List of document strings

        Returns:
            List of embedding vectors
        """
        try:
            return self.embeddings.embed_documents(documents)
        except Exception as e:
            raise RuntimeError(f"Failed to embed documents: {str(e)}")
