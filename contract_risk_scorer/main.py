"""Contract Risk Scorer FastAPI application."""

import os
import shutil
import uuid
from io import BytesIO
from typing import Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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
    brief_reason: str
    page_num: int


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


# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(title=API_TITLE, version=API_VERSION, description=API_DESCRIPTION)

# Enable CORS BEFORE adding any middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for React frontend
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve React SPA - fallback to index.html"""
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend not built")

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

        # Check API token
        if not HF_API_TOKEN:
            print("⚠️  WARNING: HF_API_TOKEN not set. LLM API will not work. Using heuristic scoring only.")
        else:
            print(f"✓ HuggingFace API token configured")

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
        status="ok",
        model="google/flan-t5-large",
        faiss_index_loaded=vectorstore is not None and vectorstore.vectorstore is not None,
        precedent_count=PrecedentSeeder.get_precedent_count(),
    )


@app.get("/api/v1/debug/contracts")
async def debug_contracts() -> Dict:
    """Debug endpoint to check contract storage."""
    return {
        "status": "ok",
        "total_contracts": len(contract_storage),
        "contracts": list(contract_storage.keys()),
        "sessions": len(session_manager.sessions) if session_manager else 0,
    }


# ============================================================================
# CONTRACT ANALYSIS ENDPOINT
# ============================================================================


@app.post("/api/v1/contract/analyze", response_model=AnalysisResponse)
async def analyze_contract(
    file: UploadFile = File(...)
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

        print(f"📄 PDF saved: {pdf_path}")

        # Parse PDF
        pages = pdf_parser.extract_clauses_text(pdf_path)

        if not pages:
            raise ValueError("No text extracted from PDF")

        print(f"📖 Extracted {len(pages)} pages from PDF")

        # Chunk contract into clauses
        chunks = clause_chunker.chunk_contract(pages, source_name=contract_id)

        if not chunks:
            raise ValueError("No clauses detected in contract")

        print(f"✂️  Chunked into {len(chunks)} clauses")

        # Score clauses
        print(f"📊 Scoring {len(chunks)} clauses...")
        risk_scores, overall_score, risk_distribution = risk_engine.score_contract(chunks)

        if not risk_scores:
            print(f"⚠️  Warning: No clauses were scored. Chunks provided: {len(chunks)}")
            # Use heuristic scoring for all chunks as fallback
            risk_scores = []
            for chunk in chunks:
                risk_score = risk_engine.score_clause(chunk)
                if risk_score:
                    risk_scores.append(risk_score)
            
            if not risk_scores:
                raise ValueError(f"Unable to score clauses. Tried LLM and heuristic methods. Chunks: {len(chunks)}")

        print(f"✓ Scored {len(risk_scores)} clauses")

        # Store contract for RAG context
        contract_storage[contract_id] = {
            "text": pages,
            "risk_scores": risk_scores,
            "overall_score": overall_score,
        }
        
        print(f"💾 Contract stored in storage. Total contracts: {len(contract_storage)}")

        # Create RAG chain for this contract
        contract_text_full = "\n\n".join(
            [rs.clause_text for rs in risk_scores]
        )
        risk_summary = f"Overall Risk: {overall_score}/100. Distribution: {risk_distribution}"

        try:
            rag_chain = RAGChain(vectorstore, contract_text_full, risk_summary)

            # Create session
            session_manager.create_session(session_id, contract_id, rag_chain, risk_scores)
            print(f"🔌 Session created: {session_id}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create RAG chain: {str(e)}")

        # Get critical clauses
        critical_clauses = [
            CriticalClause(
                clause_type=rs.clause_type,
                risk_level=rs.risk_level,
                brief_reason=rs.risk_reason[:100] + ("..." if len(rs.risk_reason) > 100 else ""),
                page_num=rs.page_num,
            )
            for rs in risk_scores
            if rs.risk_level == "CRITICAL"
        ]

        # Generate PDF report synchronously
        pdf_bytes = pdf_annotator.generate_report(contract_id, risk_scores, overall_score, risk_distribution)
        report_path = os.path.join(REPORTS_DIR, f"{contract_id}.pdf")
        with open(report_path, "wb") as f:
            f.write(pdf_bytes)

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


@app.get("/api/v1/contract/{contract_id}/clauses")
async def get_contract_clauses(contract_id: str) -> List[ClauseRisk]:
    """
    Get all risk-scored clauses for a contract.

    Args:
        contract_id: Contract identifier

    Returns:
        List of clause risk scores
    """
    print(f"📋 Fetching clauses for contract: {contract_id}")
    print(f"   Available contracts in storage: {list(contract_storage.keys())}")
    
    if contract_id not in contract_storage:
        print(f"❌ Contract {contract_id} not found in storage")
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found. Please re-analyze the contract.")

    try:
        contract_data = contract_storage[contract_id]
        risk_scores = contract_data.get("risk_scores", [])
        
        if not risk_scores:
            print(f"⚠️  Warning: Contract {contract_id} has no risk scores")
            return []

        print(f"✓ Found {len(risk_scores)} clauses for contract {contract_id}")
        print(f"   Risk levels: {[rs.risk_level for rs in risk_scores[:5]]}... (showing first 5)")
        
        clauses = []
        for rs in risk_scores:
            clause_risk = ClauseRisk(
                clause_id=rs.clause_id,
                clause_type=rs.clause_type,
                clause_text=rs.clause_text[:500],  # Truncate for API response
                risk_level=rs.risk_level,
                risk_reason=rs.risk_reason[:300],  # Truncate reason
                benchmark_position=rs.benchmark_position,
                dispute_prone=rs.dispute_prone,
                suggested_revision=rs.suggested_revision[:200],  # Truncate suggestion
                page_num=rs.page_num,
                confidence_score=rs.confidence_score,
            )
            clauses.append(clause_risk)
        
        print(f"✓ Returning {len(clauses)} properly formatted clauses")
        return clauses
    except Exception as e:
        print(f"❌ Error fetching clauses: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching clauses: {str(e)}")


# ============================================================================
# CONTRACT SUMMARY ENDPOINT
# ============================================================================


@app.get("/api/v1/contract/{contract_id}/summary")
async def get_contract_summary(contract_id: str) -> JSONResponse:
    """
    Get a concise summary of the contract.

    Args:
        contract_id: Contract identifier

    Returns:
        Summary string
    """
    if contract_id not in contract_storage:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found. Please re-analyze the contract.")

    try:
        contract_data = contract_storage[contract_id]
        risk_scores = contract_data.get("risk_scores", [])
        if not risk_scores:
            return JSONResponse({"summary": "No contract content available to summarize."})

        contract_text_full = "\n\n".join([rs.clause_text for rs in risk_scores])
        risk_summary = f"Overall Risk: {contract_data.get('overall_score', 0)}/100"

        rag_chain = RAGChain(vectorstore, contract_text_full, risk_summary)
        summary = rag_chain.summarize_contract()

        return JSONResponse({"summary": summary})
    except Exception as e:
        print(f"❌ Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


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
        # Check if RAG chain is available, create if not (lazy initialization)
        rag_chain = session.get("rag_chain")
        if not rag_chain:
            print(f"🔄 Lazy initializing RAG chain for session {session_id}")
            try:
                # Get contract data stored during session creation
                if hasattr(session_manager, '_contract_data') and session_id in session_manager._contract_data:
                    contract_data = session_manager._contract_data[session_id]
                    contract_text = contract_data['contract_text']
                    risk_summary = contract_data['risk_summary']
                    rag_chain = RAGChain(vectorstore, contract_text, risk_summary)
                    session["rag_chain"] = rag_chain
                    print(f"✓ RAG chain initialized lazily for session {session_id}")
                else:
                    print(f"⚠️  No contract data stored for lazy initialization")
                    rag_chain = None
            except Exception as e:
                print(f"⚠️  Failed to lazy-initialize RAG chain: {str(e)}")
                rag_chain = None
        
        if not rag_chain:
            # Fallback response without RAG chain
            print(f"⚠️  No RAG chain available for session {session_id}")
            referenced_clauses = []
            risk_scores = session.get("risk_scores", [])
            if risk_scores:
                # Return relevant clauses manually
                referenced_clauses = [
                    {
                        "clause_type": rs.clause_type,
                        "risk_level": rs.risk_level,
                        "page_num": rs.page_num,
                    }
                    for rs in risk_scores[:3]  # Top 3
                ]
            
            return ChatResponse(
                answer="Sorry, I cannot analyze this document at the moment. Please try again or re-upload your contract.",
                referenced_clauses=referenced_clauses,
                session_id=session_id,
            )
        
        answer_data = session_manager.ask_question(session_id, chat_input.message)

        return ChatResponse(
            answer=answer_data["answer"],
            referenced_clauses=answer_data["referenced_clauses"],
            session_id=session_id,
        )

    except Exception as e:
        print(f"❌ Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.get("/api/v1/contract/{contract_id}/session")
async def get_or_create_session(contract_id: str) -> JSONResponse:
    """
    Get or create a session for a contract.

    Args:
        contract_id: Contract identifier

    Returns:
        Session info
    """
    print(f"🔌 Getting or creating session for contract: {contract_id}")
    print(f"   Available contracts in storage: {list(contract_storage.keys())}")
    
    if contract_id not in contract_storage:
        print(f"❌ Contract {contract_id} not found in storage")
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found. Please re-analyze the contract.")

    # Check if session already exists for this contract
    existing_session = None
    for sid, session in session_manager.sessions.items():
        if session.get("contract_id") == contract_id:
            existing_session = sid
            break

    if existing_session:
        print(f"✓ Found existing session: {existing_session}")
        return JSONResponse({"session_id": existing_session, "contract_id": contract_id})

    # Create new session
    session_id = str(uuid.uuid4())
    contract_data = contract_storage[contract_id]
    risk_scores = contract_data.get("risk_scores", [])

    if not risk_scores:
        print(f"⚠️  Warning: Contract has no risk scores, creating session without RAG chain")
        session_manager.create_session(session_id, contract_id, None, [])
        return JSONResponse({"session_id": session_id, "contract_id": contract_id})

    # Create session WITHOUT RAG chain (initialize lazily on first chat message)
    print(f"✓ Creating session (RAG chain will be initialized on first chat message)")
    session_manager.create_session(session_id, contract_id, None, risk_scores)
    
    # Store contract data for lazy RAGChain initialization
    if not hasattr(session_manager, '_contract_data'):
        session_manager._contract_data = {}
    session_manager._contract_data[session_id] = {
        'contract_text': "\n\n".join([rs.clause_text for rs in risk_scores]),
        'risk_summary': f"Overall Risk: {contract_data.get('overall_score', 0)}/100"
    }

    return JSONResponse({"session_id": session_id, "contract_id": contract_id})


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
