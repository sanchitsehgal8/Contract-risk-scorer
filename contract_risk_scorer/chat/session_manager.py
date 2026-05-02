"""Session management for chat interactions."""

from datetime import datetime
from typing import Dict, List, Optional

from contract_risk_scorer.chains.rag_chain import RAGChain
from contract_risk_scorer.scoring.risk_engine import RiskScore


class SessionManager:
    """In-memory session storage for chat interactions."""

    def __init__(self):
        """Initialize session store."""
        self.sessions: Dict[str, Dict] = {}

    def create_session(
        self,
        session_id: str,
        contract_id: str,
        rag_chain: RAGChain,
        risk_scores: List[RiskScore],
    ) -> None:
        """
        Create a new chat session.

        Args:
            session_id: Unique session identifier
            contract_id: Associated contract identifier
            rag_chain: Initialized RAG chain
            risk_scores: List of risk scores for the contract
        """
        self.sessions[session_id] = {
            "session_id": session_id,
            "contract_id": contract_id,
            "rag_chain": rag_chain,
            "risk_scores": risk_scores,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "message_count": 0,
        }

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session dict or None if not found
        """
        session = self.sessions.get(session_id)

        if session:
            session["last_activity"] = datetime.now()

        return session

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            # Clear memory in RAG chain before deleting
            session = self.sessions[session_id]
            if "rag_chain" in session:
                session["rag_chain"].clear_memory()

            del self.sessions[session_id]
            return True

        return False

    def ask_question(self, session_id: str, question: str) -> Optional[Dict]:
        """
        Ask a question in a session.

        Args:
            session_id: Session identifier
            question: User question

        Returns:
            Answer dict or None if session not found
        """
        session = self.get_session(session_id)

        if not session:
            return None

        try:
            # Ask question using RAG chain
            answer_data = session["rag_chain"].ask(question)

            # Update session
            session["last_activity"] = datetime.now()
            session["message_count"] += 1

            return answer_data

        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "referenced_clauses": [],
            }

    def get_sessions_summary(self) -> Dict:
        """
        Get summary of all active sessions.

        Returns:
            Dict with session summaries
        """
        summary = {}

        for session_id, session in self.sessions.items():
            summary[session_id] = {
                "contract_id": session["contract_id"],
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat(),
                "message_count": session["message_count"],
            }

        return summary

    def get_session_count(self) -> int:
        """Get total active session count."""
        return len(self.sessions)
