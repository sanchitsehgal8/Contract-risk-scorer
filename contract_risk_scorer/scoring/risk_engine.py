"""Risk scoring engine for contract clauses."""

import json
import re
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

from langchain.llms.huggingface_hub import HuggingFaceHub
from langchain.prompts import PromptTemplate

from contract_risk_scorer.config import (
    HF_API_TOKEN,
    HF_MODEL_NAME,
    RISK_LEVELS,
    SIMILARITY_SEARCH_K,
    TEMPERATURE,
)
from contract_risk_scorer.embeddings.embedder import Embedder
from contract_risk_scorer.scoring.prompts import CLAUSE_RISK_PROMPT
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

        # Initialize HuggingFace LLM
        self.llm = HuggingFaceHub(
            repo_id=HF_MODEL_NAME,
            huggingfacehub_api_token=HF_API_TOKEN,
            task="text-generation",
            model_kwargs={"temperature": TEMPERATURE, "max_length": 512},
)

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

            # Format precedents for prompt
            precedent_texts = [
                f"- {doc.page_content}\n  Metadata: {doc.metadata}"
                for doc in precedents
            ]
            precedent_context = "\n".join(precedent_texts)

            # Build and run prompt
            prompt_input = CLAUSE_RISK_PROMPT.format(
                clause_text=clause_text, precedents=precedent_context
            )

            response = self.llm(prompt_input)

            # Parse JSON response
            risk_data = self._parse_risk_response(response)

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
        mapping = {"LOW": 20, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 100}
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
