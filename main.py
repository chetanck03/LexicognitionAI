"""Main FastAPI application for AI Viva Examiner."""
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from config import settings
from src.pdf_parser import PDFParser, PDFParserError
from src.content_analyzer import ContentAnalyzer
from src.question_generator import QuestionGenerator
from src.interview_controller import InterviewController
from src.models import Paper, KnowledgeBase

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Ensure directories exist
settings.ensure_directories()

# Initialize FastAPI app
app = FastAPI(
    title="AI Viva Examiner",
    description="Intelligent Viva Voce Examiner for Research Papers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_parser = PDFParser()
content_analyzer = ContentAnalyzer()
question_generator = QuestionGenerator()
interview_controller = InterviewController()

# Store papers and knowledge bases in memory (in production, use a database)
papers_store = {}
knowledge_bases_store = {}

# Persistence file
STORE_FILE = Path("./data/papers_store.json")

def load_stores():
    """Load papers and KBs from disk"""
    global papers_store, knowledge_bases_store
    if STORE_FILE.exists():
        try:
            import json
            with open(STORE_FILE, 'r') as f:
                data = json.load(f)
                # Convert dicts back to Paper objects
                for paper_id, paper_data in data.get('papers', {}).items():
                    papers_store[paper_id] = Paper(**paper_data)
                # KB paths stored, not the actual objects
                kb_paths = data.get('kb_paths', {})
                # Reconstruct KBs from saved vector stores
                for paper_id, vector_store_path in kb_paths.items():
                    try:
                        # Create a minimal KB object with the vector store path
                        kb = KnowledgeBase(
                            paper_id=paper_id,
                            chunks=[],
                            concepts=[],
                            vector_store_id=vector_store_path
                        )
                        knowledge_bases_store[paper_id] = kb
                    except Exception as e:
                        logger.warning(f"Could not load KB for {paper_id}: {e}")
                logger.info(f"Loaded {len(papers_store)} papers from disk")
        except Exception as e:
            logger.error(f"Error loading stores: {e}")

def save_stores():
    """Save papers and KB paths to disk"""
    try:
        import json
        STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STORE_FILE, 'w') as f:
            # Convert Paper objects to dicts for JSON serialization
            papers_dict = {}
            for paper_id, paper in papers_store.items():
                if hasattr(paper, 'model_dump'):
                    papers_dict[paper_id] = paper.model_dump(mode='json')
                else:
                    papers_dict[paper_id] = paper
            
            json.dump({
                'papers': papers_dict,
                'kb_paths': {k: v.vector_store_id if hasattr(v, 'vector_store_id') else str(v) for k, v in knowledge_bases_store.items()}
            }, f)
        logger.info(f"Saved {len(papers_store)} papers to disk")
    except Exception as e:
        logger.error(f"Error saving stores: {e}")

# Load existing data on startup
load_stores()


# Request/Response Models
class UploadResponse(BaseModel):
    paper_id: str
    title: str
    page_count: int
    message: str


class StartInterviewRequest(BaseModel):
    user_id: str
    paper_id: str


class StartInterviewResponse(BaseModel):
    session_id: str
    first_question: dict
    total_questions: int


class SubmitAnswerRequest(BaseModel):
    session_id: str
    paper_id: str
    answer: str


class SubmitAnswerResponse(BaseModel):
    evaluation: dict
    next_question: Optional[dict]
    is_complete: bool
    session_summary: Optional[dict]


@app.get("/")
async def root():
    """Serve the frontend."""
    return FileResponse("static/index.html")


@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {
        "message": "AI Viva Examiner API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """
    Upload a research paper PDF and process it.
    
    Args:
        file: PDF file to upload
        user_id: User identifier
        
    Returns:
        Upload response with paper ID and metadata
    """
    try:
        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Expected PDF, got {file.content_type}"
            )
        
        # Save uploaded file
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            
            # Check file size
            if len(content) > settings.max_file_size_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
                )
            
            f.write(content)
        
        logger.info(f"Uploaded file: {file.filename}")
        
        # Parse PDF
        parsed_doc = pdf_parser.parse(file_path)
        
        # Create paper record
        paper = Paper(
            title=parsed_doc.metadata.get('title', file.filename),
            authors=parsed_doc.metadata.get('authors', []),
            file_path=str(file_path),
            page_count=parsed_doc.metadata.get('page_count', 0)
        )
        
        # Store paper
        papers_store[paper.id] = paper
        
        # Analyze content and build knowledge base
        logger.info(f"Analyzing paper: {paper.id}")
        kb = content_analyzer.analyze(parsed_doc, paper.id)
        knowledge_bases_store[paper.id] = kb
        
        # Save to disk (convert to dict for JSON)
        try:
            save_stores()
        except Exception as e:
            logger.warning(f"Could not save stores: {e}")
        
        logger.info(f"Paper processed successfully: {paper.id}")
        logger.info(f"Papers in store: {list(papers_store.keys())}")
        logger.info(f"KBs in store: {list(knowledge_bases_store.keys())}")
        
        return UploadResponse(
            paper_id=paper.id,
            title=paper.title,
            page_count=paper.page_count,
            message="PDF uploaded and processed successfully"
        )
        
    except PDFParserError as e:
        logger.error(f"PDF parsing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/interview/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """
    Start a new interview session.
    
    Args:
        request: Start interview request with user_id and paper_id
        
    Returns:
        Session ID and first question
    """
    try:
        # Get paper and knowledge base
        paper = papers_store.get(request.paper_id)
        kb = knowledge_bases_store.get(request.paper_id)
        
        if not paper or not kb:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Get paper text for question generation
        parsed_doc = pdf_parser.parse(Path(paper.file_path))
        
        # Generate questions
        logger.info(f"Generating questions for paper: {request.paper_id}")
        questions = question_generator.generate(kb, parsed_doc.text)
        
        if len(questions) < settings.num_questions:
            logger.warning(f"Only generated {len(questions)} questions")
        
        # Start interview
        session = interview_controller.start_interview(
            request.user_id,
            request.paper_id,
            questions
        )
        
        return StartInterviewResponse(
            session_id=session.id,
            first_question=session.current_question.model_dump(),
            total_questions=len(session.questions)
        )
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interview/answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """
    Submit an answer and get evaluation.
    
    Args:
        request: Submit answer request
        
    Returns:
        Evaluation result and next question (if any)
    """
    try:
        # Get knowledge base
        logger.info(f"Looking for paper_id: {request.paper_id}")
        logger.info(f"Available papers: {list(knowledge_bases_store.keys())}")
        
        kb = knowledge_bases_store.get(request.paper_id)
        
        if not kb:
            logger.error(f"Paper not found: {request.paper_id}")
            logger.error(f"Available KBs: {list(knowledge_bases_store.keys())}")
            raise HTTPException(status_code=404, detail=f"Paper not found: {request.paper_id}. Available: {list(knowledge_bases_store.keys())}")
        
        # Submit answer and get evaluation
        evaluation = interview_controller.submit_answer(
            request.session_id,
            request.answer,
            kb
        )
        
        # Get updated session status
        status = interview_controller.get_session_status(request.session_id)
        
        is_complete = status['status'] == 'completed'
        
        response = SubmitAnswerResponse(
            evaluation=evaluation.model_dump(),
            next_question=status['current_question'],
            is_complete=is_complete,
            session_summary={
                'total_score': status['total_score'],
                'average_score': status['average_score'],
                'answers': status['answers']
            } if is_complete else None
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/interview/status/{session_id}")
async def get_session_status(session_id: str):
    """
    Get current status of an interview session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session status information
    """
    status = interview_controller.get_session_status(session_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return status


@app.post("/interview/pause/{session_id}")
async def pause_session(session_id: str):
    """Pause an active session."""
    success = interview_controller.pause_session(session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot pause session")
    
    return {"message": "Session paused successfully"}


@app.post("/interview/resume/{session_id}")
async def resume_session(session_id: str):
    """Resume a paused session."""
    success = interview_controller.resume_session(session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot resume session")
    
    return {"message": "Session resumed successfully"}


@app.get("/sessions/{user_id}")
async def list_user_sessions(user_id: str):
    """List all sessions for a user."""
    summaries = interview_controller.session_manager.list_user_sessions(user_id)
    return {"sessions": [s.model_dump(mode='json') for s in summaries]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
