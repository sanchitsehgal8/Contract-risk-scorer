"""Contract Risk Scorer FastAPI application."""

import os
import shutil
import uuid
from io import BytesIO
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from contract_risk_scorer.chains.rag_chain import RAGChain
from contract_risk_scorer.chat.session_manager import SessionManager
from contract_risk_scorer.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CONTRACTS_DIR,
    HF_API_TOKEN,
    REPORTS_DIR,
)
from contract_risk_scorer.embeddings.embedder import Embedder
from contract_risk_scorer.ingestion.clause_chunker import ClauseChunker
from contract_risk_scorer.ingestion.pdf_parser import PDFParser
from contract_risk_scorer.knowledge_base.seed_precedents import PrecedentSeeder
from contract_risk_scorer.report.pdf_annotator import PDFAnnotator
from contract_risk_scorer.scoring.risk_engine import RiskEngine, RiskScore
from contract_risk_scorer.vectorstore.faiss_store import FAISSStore

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class ClauseRisk(BaseModel):
    """Risk information for a single clause."""

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


class CriticalClause(BaseModel):
    """Summary of a critical clause."""

    clause_type: str
    risk_level: str
    risk_reason: str


class AnalysisResponse(BaseModel):
    """Response from contract analysis."""

    contract_id: str
    session_id: str
    overall_risk_score: int
    risk_distribution: Dict[str, int]
    total_clauses: int
    critical_clauses: List[CriticalClause]
    download_url: str


class ClausesResponse(BaseModel):
    """Response with all clause risks."""

    contract_id: str
    total_clauses: int
    clauses: List[ClauseRisk]


class ChatMessage(BaseModel):
    """Chat message request."""

    message: str


class ChatResponse(BaseModel):
    """Chat response."""

    answer: str
    referenced_clauses: List[Dict]
    session_id: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model: str
    faiss_index_loaded: bool
    precedent_count: int
    hf_token_present: bool


# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(title=API_TITLE, version=API_VERSION, description=API_DESCRIPTION)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL STATE
# ============================================================================

# Initialize components
embedder: Optional[Embedder] = None
vectorstore: Optional[FAISSStore] = None
risk_engine: Optional[RiskEngine] = None
pdf_parser: Optional[PDFParser] = None
clause_chunker: Optional[ClauseChunker] = None
pdf_annotator: Optional[PDFAnnotator] = None
session_manager: Optional[SessionManager] = None

# Storage for contracts and risk scores (for RAG chain context)
contract_storage: Dict[str, Dict] = {}  # contract_id -> {text, risk_scores}


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global embedder, vectorstore, risk_engine, pdf_parser, clause_chunker, pdf_annotator, session_manager

    try:
        print("🚀 Starting Contract Risk Scorer...")

        # Initialize embedder
        embedder = Embedder()
        print("✓ Embedder initialized")

        # Initialize FAISS vectorstore
        vectorstore = FAISSStore(embedder)

        # Try to load existing index, otherwise create new one from precedents
        try:
            vectorstore.load_index()
            print("✓ FAISS index loaded from disk")
        except Exception:
            print("📚 Building FAISS index from precedents...")
            precedents = PrecedentSeeder.get_precedents()
            vectorstore.build_index(precedents)
            vectorstore.save_index()
            print(f"✓ FAISS index built with {len(precedents)} precedents")

        # Initialize risk engine
        risk_engine = RiskEngine(embedder, vectorstore)
        print("✓ Risk engine initialized")

        # Initialize parsers
        pdf_parser = PDFParser()
        clause_chunker = ClauseChunker()
        print("✓ PDF parser and chunker initialized")

        # Initialize PDF annotator
        pdf_annotator = PDFAnnotator()
        print("✓ PDF annotator initialized")

        # Initialize session manager
        session_manager = SessionManager()
        print("✓ Session manager initialized")

        # Ensure storage directories exist
        os.makedirs(CONTRACTS_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)

        print("✅ Contract Risk Scorer started successfully")

    except Exception as e:
        print(f"❌ Startup error: {str(e)}")
        raise


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model="google/flan-t5-large",
        faiss_index_loaded=vectorstore is not None and vectorstore.vectorstore is not None,
        precedent_count=PrecedentSeeder.get_precedent_count(),
        hf_token_present=bool(HF_API_TOKEN),
    )


# ============================================================================
# CONTRACT ANALYSIS ENDPOINT
# ============================================================================


@app.post("/api/v1/contract/analyze", response_model=AnalysisResponse)
async def analyze_contract(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()
) -> AnalysisResponse:
    """
    Analyze a contract PDF for risk.

    Args:
        file: PDF file upload
        background_tasks: Background tasks for PDF generation

    Returns:
        Analysis response with risk scores
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    contract_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    try:
        # Save uploaded file
        pdf_path = os.path.join(CONTRACTS_DIR, f"{contract_id}.pdf")
        content = await file.read()

        with open(pdf_path, "wb") as f:
            f.write(content)

        # Parse PDF
        pages = pdf_parser.extract_clauses_text(pdf_path)

        if not pages:
            raise ValueError("No text extracted from PDF")

        # Chunk contract into clauses
        chunks = clause_chunker.chunk_contract(pages, source_name=contract_id)

        if not chunks:
            raise ValueError("No clauses detected in contract")

        # Score clauses
        risk_scores, overall_score, risk_distribution = risk_engine.score_contract(chunks)

        if not risk_scores:
            raise ValueError("Unable to score contract clauses")

        # Store contract for RAG context
        contract_storage[contract_id] = {
            "text": pages,
            "risk_scores": risk_scores,
            "overall_score": overall_score,
        }

        # Create RAG chain for this contract
        contract_text_full = "\n\n".join(
            [rs.clause_text for rs in risk_scores]
        )
        risk_summary = f"Overall Risk: {overall_score}/100. Distribution: {risk_distribution}"

        try:
            rag_chain = RAGChain(vectorstore, contract_text_full, risk_summary)

            # Create session
            session_manager.create_session(session_id, contract_id, rag_chain, risk_scores)
        except Exception as e:
            print(f"Warning: Could not create RAG chain: {str(e)}")

        # Get critical clauses
        critical_clauses = [
            CriticalClause(
                clause_type=rs.clause_type,
                risk_level=rs.risk_level,
                risk_reason=rs.risk_reason,
            )
            for rs in risk_scores
            if rs.risk_level == "CRITICAL"
        ]

        # Generate PDF report in background
        background_tasks.add_task(
            _generate_report_background, contract_id, risk_scores, overall_score, risk_distribution
        )

        download_url = f"/api/v1/contract/{contract_id}/report"

        return AnalysisResponse(
            contract_id=contract_id,
            session_id=session_id,
            overall_risk_score=overall_score,
            risk_distribution=risk_distribution,
            total_clauses=len(risk_scores),
            critical_clauses=critical_clauses[:3],  # Top 3
            download_url=download_url,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing contract: {str(e)}")


def _generate_report_background(
    contract_id: str,
    risk_scores: List[RiskScore],
    overall_score: int,
    risk_distribution: Dict,
) -> None:
    """Generate PDF report in background."""
    try:
        pdf_bytes = pdf_annotator.generate_report(contract_id, risk_scores, overall_score, risk_distribution)

        report_path = os.path.join(REPORTS_DIR, f"{contract_id}.pdf")
        with open(report_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"✓ Report generated: {report_path}")

    except Exception as e:
        print(f"Error generating report: {str(e)}")


# ============================================================================
# GET REPORT ENDPOINT
# ============================================================================


@app.get("/api/v1/contract/{contract_id}/report")
async def get_report(contract_id: str) -> FileResponse:
    """
    Download annotated PDF report.

    Args:
        contract_id: Contract identifier

    Returns:
        PDF file
    """
    report_path = os.path.join(REPORTS_DIR, f"{contract_id}.pdf")

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found. Please check the analysis endpoint.")

    return FileResponse(
        path=report_path,
        filename=f"contract_risk_report_{contract_id}.pdf",
        media_type="application/pdf",
    )


# ============================================================================
# GET CLAUSES ENDPOINT
# ============================================================================


@app.get("/api/v1/contract/{contract_id}/clauses", response_model=ClausesResponse)
async def get_contract_clauses(contract_id: str) -> ClausesResponse:
    """
    Get all risk-scored clauses for a contract.

    Args:
        contract_id: Contract identifier

    Returns:
        List of clause risk scores
    """
    if contract_id not in contract_storage:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract_data = contract_storage[contract_id]
    risk_scores = contract_data["risk_scores"]

    clauses = [
        ClauseRisk(
            clause_id=rs.clause_id,
            clause_type=rs.clause_type,
            clause_text=rs.clause_text,
            risk_level=rs.risk_level,
            risk_reason=rs.risk_reason,
            benchmark_position=rs.benchmark_position,
            dispute_prone=rs.dispute_prone,
            suggested_revision=rs.suggested_revision,
            page_num=rs.page_num,
            confidence_score=rs.confidence_score,
        )
        for rs in risk_scores
    ]

    return ClausesResponse(
        contract_id=contract_id,
        total_clauses=len(clauses),
        clauses=clauses,
    )


# ============================================================================
# CHAT ENDPOINTS
# ============================================================================


@app.post("/api/v1/chat/{session_id}/message", response_model=ChatResponse)
async def send_chat_message(session_id: str, chat_input: ChatMessage) -> ChatResponse:
    """
    Send a message in a chat session.

    Args:
        session_id: Session identifier
        chat_input: Chat message

    Returns:
        Chat response with answer
    """
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        answer_data = session_manager.ask_question(session_id, chat_input.message)

        return ChatResponse(
            answer=answer_data["answer"],
            referenced_clauses=answer_data["referenced_clauses"],
            session_id=session_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.delete("/api/v1/chat/{session_id}")
async def delete_session(session_id: str) -> JSONResponse:
    """
    Delete a chat session.

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    if not session_manager.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    session_manager.delete_session(session_id)

    return JSONResponse({"status": "success", "message": "Session deleted"})


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@app.get("/api/v1/sessions")
async def get_all_sessions() -> JSONResponse:
    """Get summary of all active sessions."""
    summary = session_manager.get_sessions_summary()
    return JSONResponse({"session_count": len(summary), "sessions": summary})


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return JSONResponse(
        {
            "name": "Contract Risk Scorer API",
            "version": API_VERSION,
            "status": "running",
            "docs": "/docs",
            "health": "/api/v1/health",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
