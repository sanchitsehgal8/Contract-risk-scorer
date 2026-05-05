"""Clause chunking and metadata extraction."""

import re
import uuid
from typing import Dict, List

from langchain.text_splitter import RecursiveCharacterTextSplitter

from contract_risk_scorer.config import CHUNK_OVERLAP, CHUNK_SIZE, CLAUSE_TYPES


class ClauseChunker:
    """Split contracts into clause-level chunks with metadata."""

    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        """
        Initialize chunker.

        Args:
            chunk_size: Size of each chunk
            overlap: Number of overlapping characters between chunks
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.clause_patterns = self._build_clause_patterns()

    @staticmethod
    def _build_clause_patterns() -> Dict[str, List[str]]:
        """
        Build regex patterns for clause type detection.

        Returns:
            Dict mapping clause types to keyword patterns
        """
        return {
            "Termination": [
                r"(?:terminate|termination|end of)",
                r"either party may terminate",
                r"grounds? for termination",
            ],
            "Liability Cap": [
                r"liability cap",
                r"cap on liability",
                r"limitation of liability",
                r"maximum liability",
            ],
            "IP Assignment": [
                r"(?:intellectual property|ip) (?:assignment|assign)",
                r"(?:copyright|trademark|patent) assign",
                r"ownership of (?:intellectual property|ip)",
            ],
            "Non-Compete": [
                r"non-compete|non-competition",
                r"covenant not to compete",
                r"restrictive covenant",
            ],
            "Indemnification": [
                r"indemnif",
                r"hold harmless",
                r"defend against claims",
            ],
            "Governing Law": [
                r"governing law",
                r"subject to .*? law",
                r"jurisdiction",
            ],
            "Payment Terms": [
                r"payment (?:terms|schedule|amount)",
                r"invoice|billing",
                r"payment shall be",
            ],
            "Confidentiality": [
                r"confidential|confidentiality",
                r"nondisclosure|non-disclosure",
                r"secret information",
            ],
            "Data Privacy": [
                r"(?:data privacy|privacy|gdpr|ccpa)",
                r"personal (?:information|data)",
                r"data protection",
            ],
            "Arbitration": [
                r"arbitrat",
                r"dispute resolution",
                r"arbitrator",
            ],
            "Equity Vesting": [
                r"equity|vesting|stock option",
                r"share grant",
                r"option pool",
            ],
            "Change of Control": [
                r"change of control",
                r"acquisition|merger",
                r"sale of company",
            ],
        }

    def chunk_contract(
        self, contract_text: str, source_name: str = "contract"
    ) -> List[Dict]:
        """
        Split contract into chunks with clause metadata.

        Args:
            contract_text: Full contract text
            source_name: Name/identifier for the contract

        Returns:
            List of chunk dicts with metadata
        """
        # Split into chunks using LangChain splitter
        chunks = self.splitter.split_text(contract_text)

        results = []
        char_position = 0

        for chunk_index, chunk_text in enumerate(chunks):
            # Detect clause type
            clause_type = self._detect_clause_type(chunk_text)

            # Find where this chunk starts in original text
            try:
                char_start = contract_text.find(chunk_text, char_position)
                if char_start == -1:
                    char_start = char_position

                char_end = char_start + len(chunk_text)
            except Exception:
                char_start = char_position
                char_end = char_position + len(chunk_text)

            chunk_id = str(uuid.uuid4())

            results.append(
                {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "clause_type": clause_type,
                    "page_num": self._estimate_page_num(char_start, contract_text),
                    "char_start": char_start,
                    "char_end": char_end,
                    "source": source_name,
                    "chunk_index": chunk_index,
                }
            )

            char_position = char_end

        return results

    def _detect_clause_type(self, text: str) -> str:
        """
        Detect clause type from text using keyword matching.

        Args:
            text: Chunk text

        Returns:
            Detected clause type, defaults to "General"
        """
        text_lower = text.lower()

        for clause_type, patterns in self.clause_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return clause_type

        return "General"

    @staticmethod
    def _estimate_page_num(char_position: int, full_text: str) -> int:
        """
        Estimate page number based on character position.

        Args:
            char_position: Character position in text
            full_text: Full contract text

        Returns:
            Estimated page number
        """
        # Assume ~3000 characters per page on average
        chars_per_page = 3000
        page_num = max(1, (char_position // chars_per_page) + 1)
        return page_num
