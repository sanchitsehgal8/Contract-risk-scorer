"""Risk scoring engine for contract clauses."""

import json
import re
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

from contract_risk_scorer.config import (
    RISK_LEVELS,
    SIMILARITY_SEARCH_K,
)
from contract_risk_scorer.embeddings.embedder import Embedder
from contract_risk_scorer.vectorstore.faiss_store import FAISSStore


@dataclass
class RiskScore:
    """Risk score for a contract clause."""

    clause_id: str
    clause_type: str
    clause_text: str
    risk_level: str
    risk_reason: str
    benchmark_position: str
    dispute_prone: bool
    suggested_revision: str
    page_num: int
    confidence_score: float


class RiskEngine:
    """Scoring engine for contract risk assessment."""

    def __init__(self, embedder: Embedder, vectorstore: FAISSStore):
        """
        Initialize risk engine.

        Args:
            embedder: Embedder for semantic search
            vectorstore: FAISS vectorstore with precedents
        """
        self.embedder = embedder
        self.vectorstore = vectorstore

    def score_clause(self, clause: Dict) -> Optional[RiskScore]:
        """
        Score a single clause for risk.

        Args:
            clause: Clause dict with text, type, page_num, etc.

        Returns:
            RiskScore object or None if scoring fails
        """
        try:
            clause_text = clause["text"]
            clause_type = clause.get("clause_type", "General")
            page_num = clause.get("page_num", 0)
            chunk_id = clause.get("chunk_id", str(uuid.uuid4()))

            # Retrieve similar precedents
            precedents = self.vectorstore.search(clause_text, k=SIMILARITY_SEARCH_K)

            # Skip LLM - use heuristic scoring directly (100% reliable)
            print(f"✓ Using heuristic scoring (no external LLM dependency)")
            risk_data = self._heuristic_scoring(clause_text, clause_type, precedents)

            if risk_data is None:
                return None

            risk_score = RiskScore(
                clause_id=chunk_id,
                clause_type=clause_type,
                clause_text=clause_text,
                risk_level=risk_data.get("risk_level", "MEDIUM"),
                risk_reason=risk_data.get("risk_reason", "Unable to determine"),
                benchmark_position=risk_data.get("benchmark_position", "market_standard"),
                dispute_prone=risk_data.get("dispute_prone", False),
                suggested_revision=risk_data.get(
                    "suggested_revision", "Review with legal counsel"
                ),
                page_num=page_num,
                confidence_score=risk_data.get("confidence_score", 0.5),
            )

            return risk_score

        except Exception as e:
            print(f"Error scoring clause: {str(e)}")
            return None

    def _heuristic_scoring(self, clause_text: str, clause_type: str, precedents: List) -> Dict:
        """
        Heuristic scoring when LLM is unavailable.
        
        Args:
            clause_text: Text of the clause
            clause_type: Type of clause
            precedents: Retrieved precedent documents
        
        Returns:
            Risk data dictionary
        """
        clause_lower = clause_text.lower()

        # Weighted keyword scoring
        risk_keywords = {
            "no liability": 35,
            "unlimited": 30,
            "full liability": 30,
            "indemnify": 22,
            "indemnification": 22,
            "liability": 18,
            "penalty": 16,
            "consequential": 16,
            "damages": 14,
            "breach": 12,
            "terminate": 12,
            "termination": 12,
            "auto-renew": 10,
            "non-compete": 12,
            "exclusive": 10,
            "audit": 10,
            "warranty": 10,
            "dispute": 10,
            "litigation": 18,
            "arbitration": 10,
            "governing law": 8,
            "ip": 10,
            "intellectual property": 12,
            "assignment": 8,
            "subcontract": 8,
            "data": 8,
            "privacy": 10,
            "security": 10,
        }

        positive_keywords = {
            "limited liability": -18,
            "cap on liability": -16,
            "liability cap": -16,
            "mutual": -8,
            "reasonable efforts": -8,
            "industry standard": -6,
            "as permitted by law": -6,
        }

        score = 0
        matched_keywords = []
        for keyword, weight in risk_keywords.items():
            if keyword in clause_lower:
                score += weight
                matched_keywords.append(keyword)

        for keyword, weight in positive_keywords.items():
            if keyword in clause_lower:
                score += weight

        # Clause type weighting
        clause_type_weights = {
            "liability": 15,
            "indemnity": 15,
            "termination": 12,
            "confidentiality": 8,
            "ip": 12,
            "governing law": 6,
            "dispute": 10,
            "payment": 8,
            "audit": 6,
            "data": 10,
            "insurance": 6,
            "force majeure": 6,
        }
        clause_key = clause_type.lower()
        for key, weight in clause_type_weights.items():
            if key in clause_key:
                score += weight
                break

        # Base score if nothing matched
        if score == 0:
            score = 6

        # Map score to risk level and confidence
        if score >= 55:
            risk_level = "CRITICAL"
            confidence = 0.85
        elif score >= 40:
            risk_level = "HIGH"
            confidence = 0.75
        elif score >= 22:
            risk_level = "MEDIUM"
            confidence = 0.6
        else:
            risk_level = "LOW"
            confidence = 0.45
        
        # Check precedents for benchmark
        benchmark_position = "market_standard"
        dispute_prone = False
        if precedents:
            for precedent in precedents:
                if hasattr(precedent, 'metadata'):
                    meta = precedent.metadata
                    if meta.get('benchmark') == 'above_market':
                        benchmark_position = "above_market"
                        score += 6
                    if meta.get('dispute_history'):
                        dispute_prone = True
                        score += 6

        # Re-evaluate risk after precedent adjustments
        if score >= 55:
            risk_level = "CRITICAL"
            confidence = max(confidence, 0.85)
        elif score >= 40:
            risk_level = "HIGH"
            confidence = max(confidence, 0.75)
        elif score >= 22:
            risk_level = "MEDIUM"
            confidence = max(confidence, 0.6)
        
        return {
            "risk_level": risk_level,
            "risk_reason": f"Heuristic analysis of {clause_type} clause. Keyword hits: {', '.join(matched_keywords) if matched_keywords else 'none'}.",
            "benchmark_position": benchmark_position,
            "dispute_prone": dispute_prone,
            "suggested_revision": f"Review {clause_type} against market standards and legal precedents.",
            "confidence_score": confidence,
        }

    def score_contract(self, chunks: List[Dict]) -> tuple:
        """
        Score all clauses in a contract.

        Args:
            chunks: List of clause chunks

        Returns:
            Tuple of (risk_scores, aggregate_score, risk_distribution)
        """
        risk_scores = []
        risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        total_risk_points = 0

        for chunk in chunks:
            risk_score = self.score_clause(chunk)

            if risk_score:
                risk_scores.append(risk_score)
                risk_distribution[risk_score.risk_level] += 1

                # Calculate points for aggregate scoring
                risk_points = self._risk_level_to_points(risk_score.risk_level)
                total_risk_points += risk_points * risk_score.confidence_score

        # Calculate overall risk score (0-100)
        if risk_scores:
            avg_risk = total_risk_points / len(risk_scores)
            overall_score = min(100, int(avg_risk))
        else:
            overall_score = 0

        return risk_scores, overall_score, risk_distribution

    @staticmethod
    def _risk_level_to_points(risk_level: str) -> int:
        """Convert risk level to numeric points."""
        mapping = {"LOW": 15, "MEDIUM": 50, "HIGH": 80, "CRITICAL": 95}
        return mapping.get(risk_level, 50)

    @staticmethod
    def _parse_risk_response(response: str) -> Optional[Dict]:
        """
        Parse JSON response from LLM.

        Args:
            response: LLM response text

        Returns:
            Parsed dict or None if parsing fails
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)

            if not json_match:
                return None

            json_str = json_match.group(0)
            data = json.loads(json_str)

            # Validate required fields
            required_fields = [
                "risk_level",
                "risk_reason",
                "benchmark_position",
                "dispute_prone",
                "suggested_revision",
                "confidence_score",
            ]

            for field in required_fields:
                if field not in data:
                    return None

            # Validate risk level
            if data["risk_level"] not in RISK_LEVELS:
                data["risk_level"] = "MEDIUM"

            # Validate benchmark position
            valid_benchmarks = ["market_standard", "above_market", "below_market"]
            if data["benchmark_position"] not in valid_benchmarks:
                data["benchmark_position"] = "market_standard"

            # Ensure confidence score is between 0 and 1
            data["confidence_score"] = max(0, min(1, float(data["confidence_score"])))

            return data

        except Exception as e:
            print(f"Error parsing risk response: {str(e)}")
            return None
