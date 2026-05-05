

from typing import Dict, List

from huggingface_hub import InferenceClient
from langchain.schema import Document
from langchain.vectorstores import FAISS

from contract_risk_scorer.config import HF_CHAT_MODEL, HF_TOKEN, RETRIEVER_SEARCH_K
from contract_risk_scorer.ingestion.clause_chunker import ClauseChunker
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
        self.contract_vectorstore = None
        self.contract_retriever = None
        
        # Initialize Hugging Face client if token is available
        self.client = None
        if HF_TOKEN:
            self.client = InferenceClient(api_key=HF_TOKEN)

        # Build a contract-specific vectorstore for accurate retrieval
        try:
            chunker = ClauseChunker()
            chunks = chunker.chunk_contract(contract_context, source_name="contract")
            documents = [
                Document(
                    page_content=chunk["text"],
                    metadata={
                        "clause_type": chunk["clause_type"],
                        "page_num": chunk["page_num"],
                        "chunk_id": chunk["chunk_id"],
                        "source": chunk["source"],
                    },
                )
                for chunk in chunks
            ]
            if documents:
                self.contract_vectorstore = FAISS.from_documents(
                    documents=documents,
                    embedding=self.vectorstore.embedder.embeddings,
                )
                self.contract_retriever = self.contract_vectorstore.as_retriever(
                    search_kwargs={"k": RETRIEVER_SEARCH_K}
                )
        except Exception as e:
            print(f"⚠️  Failed to build contract vectorstore: {str(e)[:80]}")

        # Store chat history
        self.chat_history = []

    def ask(self, question: str) -> Dict:
        """
        Ask a question about the contract using RAG with intelligent fallback.

        Args:
            question: User question

        Returns:
            Dict with answer and referenced clauses
        """
        try:
            # Store question in history
            self.chat_history.append({"role": "user", "content": question})
            
            # Create retriever from contract-specific vectorstore
            retriever = self.contract_retriever
            if retriever is None:
                retriever = self.vectorstore.vectorstore.as_retriever(
                    search_kwargs={"k": RETRIEVER_SEARCH_K}
                )
            
            # Retrieve relevant documents
            print(f"🔍 Retrieving documents for: {question[:50]}...")
            try:
                docs = retriever.invoke(question)
            except AttributeError:
                docs = retriever.get_relevant_documents(question)
            print(f"✓ Retrieved {len(docs)} relevant documents")
            
            if not docs:
                answer = "I couldn't find relevant information in the contract to answer your question."
                self.chat_history.append({"role": "assistant", "content": answer})
                return {
                    "answer": answer,
                    "referenced_clauses": [],
                    "chat_history_length": len(self.chat_history),
                }
            
            # Extract smart answer from documents (fallback-first approach)
            answer = self._extract_answer_from_documents(question, docs)
            
            print(f"✓ Answer generated: {str(answer)[:80]}...")
            
            # Store answer in history
            self.chat_history.append({"role": "assistant", "content": str(answer)})
            
            # Extract clause references
            referenced_clauses = [
                {
                    "text": doc.page_content[:150],
                    "metadata": doc.metadata,
                }
                for doc in docs[:3]
            ]
            
            return {
                "answer": str(answer),
                "referenced_clauses": referenced_clauses,
                "chat_history_length": len(self.chat_history),
            }

        except Exception as e:
            print(f"❌ Error in ask(): {str(e)}")
            import traceback
            traceback.print_exc()
            error_msg = "Unable to process question at this time. Please try again."
            self.chat_history.append({"role": "assistant", "content": error_msg})
            return {
                "answer": error_msg,
                "referenced_clauses": [],
                "chat_history_length": len(self.chat_history),
            }

    def summarize_contract(self) -> str:
        """Generate a concise summary of the contract."""
        try:
            if not self.contract_context:
                return "No contract content available to summarize."

            context = self._build_summary_context(self.contract_context)

            retriever = self.contract_retriever
            if retriever is None:
                retriever = self.vectorstore.vectorstore.as_retriever(
                    search_kwargs={"k": RETRIEVER_SEARCH_K}
                )

            if self.client:
                system_prompt = (
                    "You are a legal AI assistant. Summarize the contract in 2-4 sentences. "
                    "Focus on purpose, parties, key obligations, and any notable risk terms."
                )
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "system", "content": f"Contract Text:\n{context}"},
                    {"role": "user", "content": "Summarize the contract."},
                ]
                try:
                    completion = self.client.chat.completions.create(
                        model=HF_CHAT_MODEL,
                        messages=messages,
                        max_tokens=240,
                        temperature=0.2,
                    )
                    message = completion.choices[0].message
                    answer = getattr(message, "content", "")
                    if not answer and isinstance(message, dict):
                        answer = message.get("content", "")
                    answer = (answer or "").strip()
                    if answer:
                        return answer
                except Exception as e:
                    print(f"⚠️  Summary LLM call failed, using fallback: {str(e)[:80]}")

            # Fallback: return first few meaningful sentences from contract text
            sentences = [s.strip() for s in context.split('.') if len(s.strip()) > 20]
            if sentences:
                return ". ".join(sentences[:3]) + "."
            return "Unable to summarize the contract at this time."
        except Exception as e:
            print(f"❌ Error in summarize_contract(): {str(e)}")
            return "Unable to summarize the contract at this time."

    @staticmethod
    def _build_summary_context(text: str) -> str:
        """Build a compact context window for summarization."""
        cleaned = text.strip()
        if len(cleaned) <= 8000:
            return cleaned

        head = cleaned[:4000]
        tail = cleaned[-4000:]
        return f"{head}\n\n...\n\n{tail}"

    def _extract_answer_from_documents(self, question: str, docs: List) -> str:
        """
        Extract an intelligent answer from retrieved documents.
        Tries LLM first, falls back to smart extraction.

        Args:
            question: User question
            docs: Retrieved documents

        Returns:
            Generated answer
        """
        # Try LLM first
        llm_answer = self._try_llm_answer(question, docs)
        if llm_answer:
            return llm_answer
        
        # Fallback: Smart extraction from documents
        return self._smart_extraction(question, docs)

    def _try_llm_answer(self, question: str, docs: List) -> str:
        """Use LLM for answers; return None if it fails."""
        if not self.client:
            return None

        context = "\n\n".join(
            [f"Document {i + 1}:\n{doc.page_content}" for i, doc in enumerate(docs[:4])]
        )

        system_prompt = (
            "You are a legal AI assistant. Answer using only the provided contract sections. "
            "If the answer is not in the context, say you do not have enough information. "
            "Be concise, specific, and cite details present in the text."
        )

        # Include brief recent history (excluding the current question already passed)
        history = self.chat_history[-6:-1] if len(self.chat_history) > 1 else []

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "system",
                "content": (
                    f"Contract Risk Summary: {self.risk_summary}\n\n"
                    f"Relevant Contract Sections:\n{context}"
                ),
            },
        ]

        messages.extend(history)
        messages.append({"role": "user", "content": question})

        try:
            completion = self.client.chat.completions.create(
                model=HF_CHAT_MODEL,
                messages=messages,
                max_tokens=400,
                temperature=0.2,
            )
            message = completion.choices[0].message
            answer = getattr(message, "content", "")
            if not answer and isinstance(message, dict):
                answer = message.get("content", "")
            answer = (answer or "").strip()
            if answer and len(answer) > 10:
                return answer
        except Exception as e:
            print(f"⚠️  LLM call failed, using smart extraction: {str(e)[:80]}")

        return None

    @staticmethod
    def _smart_extraction(question: str, docs: List) -> str:
        """
        Smart extraction strategy when LLM is unavailable.
        Combines keyword matching, summarization, and context extraction.
        """
        # Keywords that indicate what the user is asking about
        question_lower = question.lower()
        
        # Check if question asks about a specific clause type
        clause_keywords = {
            "payment": "payment terms",
            "liability": "liability limitations",
            "termination": "contract termination",
            "confidentiality": "confidentiality obligations",
            "ip": "intellectual property",
            "governing": "governing law",
            "dispute": "dispute resolution",
            "indemnity": "indemnification",
            "audit": "audit rights",
            "data": "data privacy",
            "insurance": "insurance requirements",
            "force majeure": "force majeure",
        }
        
        matched_keyword = None
        for keyword, description in clause_keywords.items():
            if keyword in question_lower:
                matched_keyword = description
                break
        
        # Build answer from documents
        answer_parts = []
        
        # Add matched clause info if found
        if matched_keyword:
            answer_parts.append(f"Regarding {matched_keyword}:")
        
        # Extract first meaningful sentence from each top doc
        for i, doc in enumerate(docs[:2]):
            text = doc.page_content.strip()
            # Get first sentence
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
            if sentences:
                answer_parts.append(sentences[0] + ".")
        
        if answer_parts:
            answer = " ".join(answer_parts)
            # Clean up and truncate
            answer = answer[:300] + "..." if len(answer) > 300 else answer
            return answer
        
        # Last resort: generic response
        return f"Based on the contract, the relevant sections indicate: {docs[0].page_content[:150]}..."

    def get_history(self) -> List:
        """
        Get conversation history.

        Returns:
            List of conversation messages
        """
        return self.chat_history

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.chat_history = []
