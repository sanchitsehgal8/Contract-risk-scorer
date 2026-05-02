"""RAG chain for contract analysis chatbot."""

from typing import Dict, List, Optional

from langchain.chains import ConversationalRetrievalChain
from langchain.llms.huggingface_hub import HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from contract_risk_scorer.config import HF_API_TOKEN, HF_MODEL_NAME, RETRIEVER_SEARCH_K
from contract_risk_scorer.scoring.prompts import CHAT_COMBINE_DOCUMENTS_PROMPT
from contract_risk_scorer.vectorstore.faiss_store import FAISSStore


class RAGChain:
    """Retrieval-Augmented Generation chain for contract Q&A."""

    def __init__(self, vectorstore: FAISSStore, contract_context: str, risk_summary: str):
        """
        Initialize RAG chain.

        Args:
            vectorstore: FAISS vectorstore with contract and precedents
            contract_context: Full contract text
            risk_summary: Risk assessment summary
        """
        self.vectorstore = vectorstore
        self.contract_context = contract_context
        self.risk_summary = risk_summary

        # Initialize memory for conversation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="answer"
        )

        # Initialize LLM
        self.llm = HuggingFaceHub(
            repo_id=HF_MODEL_NAME,
            huggingfacehub_api_token=HF_API_TOKEN,
            model_kwargs={"temperature": 0.3, "max_length": 512},
        )

        # Create retriever from vectorstore
        self.retriever = vectorstore.vectorstore.as_retriever(
            search_kwargs={"k": RETRIEVER_SEARCH_K}
        )

        # Build conversational retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={
                "prompt": CHAT_COMBINE_DOCUMENTS_PROMPT,
            },
            verbose=False,
        )

    def ask(self, question: str) -> Dict:
        """
        Ask a question about the contract.

        Args:
            question: User question

        Returns:
            Dict with answer and referenced clauses
        """
        try:
            # Enhance question with contract context
            enhanced_question = f"Based on the contract provided, {question}"

            # Run the chain
            result = self.chain({"question": enhanced_question})

            # Extract answer and source documents
            answer = result.get("answer", "Unable to answer the question.")
            source_docs = result.get("source_documents", [])

            # Extract clause references from sources
            referenced_clauses = [
                {
                    "text": doc.page_content[:200],
                    "metadata": doc.metadata,
                }
                for doc in source_docs
            ]

            return {
                "answer": answer,
                "referenced_clauses": referenced_clauses,
                "chat_history_length": len(self.memory.buffer_as_messages),
            }

        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "referenced_clauses": [],
                "chat_history_length": 0,
            }

    def get_history(self) -> List:
        """
        Get conversation history.

        Returns:
            List of conversation messages
        """
        return self.memory.buffer_as_messages

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
