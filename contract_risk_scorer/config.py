"""Configuration and constants for Contract Risk Scorer."""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
HF_TOKEN: str = os.getenv("HF_TOKEN", HF_API_TOKEN)
HF_MODEL_NAME: str = os.getenv("HF_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
HF_CHAT_MODEL: str = os.getenv("HF_CHAT_MODEL", "meta-llama/Llama-3.1-8B-Instruct:novita")
EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

# FAISS Configuration
FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "/tmp/faiss_index")
FAISS_METADATA_PATH: str = os.getenv("FAISS_METADATA_PATH", "/tmp/faiss_metadata")

# Storage Configuration
CONTRACTS_DIR: str = os.getenv("CONTRACTS_DIR", "/tmp/contracts")
REPORTS_DIR: str = os.getenv("REPORTS_DIR", "/tmp/reports")

# Ensure storage directories exist
Path(CONTRACTS_DIR).mkdir(parents=True, exist_ok=True)
Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
Path(FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)

# Risk Levels
RISK_LEVELS: List[str] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Clause Types
CLAUSE_TYPES: List[str] = [
    "Termination",
    "Liability Cap",
    "IP Assignment",
    "Non-Compete",
    "Indemnification",
    "Governing Law",
    "Payment Terms",
    "Confidentiality",
    "Data Privacy",
    "Arbitration",
    "Equity Vesting",
    "Change of Control",
]

# Processing Configuration
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 100
SIMILARITY_SEARCH_K: int = 5
RETRIEVER_SEARCH_K: int = 6

# Model Configuration
TEMPERATURE: float = 0.3
MAX_LENGTH: int = 512
MIN_LENGTH: int = 100

# Timeout Configuration
HF_API_TIMEOUT: int = 30

# FastAPI Configuration
API_TITLE: str = "Contract Risk Scorer API"
API_VERSION: str = "1.0.0"
API_DESCRIPTION: str = "Advanced contract risk analysis and scoring system"

# Risk Score Thresholds
RISK_SCORE_RANGES = {
    "CRITICAL": (80, 100),
    "HIGH": (60, 79),
    "MEDIUM": (40, 59),
    "LOW": (0, 39),
}

# Confidence Score Thresholds
CONFIDENCE_THRESHOLD: float = 0.7
