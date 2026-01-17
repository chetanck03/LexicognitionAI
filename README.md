# AI Viva Examiner

An intelligent Viva Voce Examiner system that ingests research papers (PDFs) and conducts live oral examinations to test understanding.

## Features

- 📄 PDF upload and intelligent text extraction
- 🤖 AI-powered question generation (5 conceptual questions per paper)
- 💬 Interactive interview sessions
- ✅ Automated answer evaluation with scoring (1-10)
- 📊 Session tracking and history
- 🔍 RAG-based fact-checking against paper content

## Architecture

The system uses a modular, production-ready architecture:

- **PDF Parser**: Extracts text from research papers
- **Content Analyzer**: Builds knowledge base using RAG (Retrieval-Augmented Generation)
- **Question Generator**: Creates paper-specific conceptual questions using LLM
- **Answer Evaluator**: Scores answers and checks correctness
- **Interview Controller**: Manages examination flow
- **Session Manager**: Persists session data

## Setup

### Prerequisites

- Python 3.10+
- Groq API key (already configured!) or OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-viva-examiner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

**Good news!** Your Groq API key is already configured in `.env`. The system uses:
- **Groq API** for LLM (question generation & evaluation) - Ultra fast! ⚡
- **OpenAI API** for embeddings (optional - can use free alternatives)

If you want to use OpenAI instead, edit `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your_key_here
```

### Configuration

All settings are managed through environment variables in `.env`:

- **API Keys**: OpenAI API key
- **LLM Settings**: Model, temperature, max tokens
- **File Upload**: Max file size, allowed types
- **Question Generation**: Number of questions, timeout
- **Evaluation**: Score range, timeout
- **Storage**: Database path, vector store path
- **Server**: Host, port, CORS origins

See `.env.example` for all available options.

## Usage

### Start the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API docs: `http://localhost:8000/docs`

### API Endpoints

#### 1. Upload PDF
```bash
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- user_id: User identifier

Response:
{
  "paper_id": "uuid",
  "title": "Paper Title",
  "page_count": 10,
  "message": "PDF uploaded and processed successfully"
}
```

#### 2. Start Interview
```bash
POST /interview/start
Content-Type: application/json

{
  "user_id": "user123",
  "paper_id": "paper-uuid"
}

Response:
{
  "session_id": "session-uuid",
  "first_question": {
    "id": "q1",
    "text": "Why does the paper propose...",
    "type": "why",
    ...
  },
  "total_questions": 5
}
```

#### 3. Submit Answer
```bash
POST /interview/answer
Content-Type: application/json

{
  "session_id": "session-uuid",
  "paper_id": "paper-uuid",
  "answer": "The paper proposes this because..."
}

Response:
{
  "evaluation": {
    "score": 8,
    "correctness": "correct",
    "feedback": "Good answer...",
    "factual_errors": [],
    "missing_concepts": []
  },
  "next_question": {...},
  "is_complete": false,
  "session_summary": null
}
```

#### 4. Get Session Status
```bash
GET /interview/status/{session_id}

Response:
{
  "session_id": "uuid",
  "status": "in_progress",
  "current_question_index": 2,
  "total_questions": 5,
  "questions_remaining": 3,
  "current_question": {...},
  "answers": [...],
  "total_score": 15,
  "average_score": 7.5
}
```

## Example Usage with cURL

```bash
# 1. Upload a PDF
curl -X POST "http://localhost:8000/upload" \
  -F "file=@research_paper.pdf" \
  -F "user_id=user123"

# 2. Start interview
curl -X POST "http://localhost:8000/interview/start" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","paper_id":"<paper_id>"}'

# 3. Submit answer
curl -X POST "http://localhost:8000/interview/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"<session_id>",
    "paper_id":"<paper_id>",
    "answer":"Your answer here..."
  }'
```

## Project Structure

```
.
├── config.py                 # Configuration management
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── src/
│   ├── __init__.py
│   ├── models.py            # Data models
│   ├── pdf_parser.py        # PDF parsing
│   ├── content_analyzer.py  # RAG pipeline
│   ├── question_generator.py # Question generation
│   ├── answer_evaluator.py  # Answer evaluation
│   ├── interview_controller.py # Interview flow
│   └── session_manager.py   # Session persistence
├── data/                    # Data storage (created automatically)
│   ├── uploads/            # Uploaded PDFs
│   ├── vector_store/       # Vector embeddings
│   └── sessions.db         # Session database
└── logs/                   # Application logs
```

## Production Deployment

### Environment Variables

Ensure all sensitive data is in environment variables:
- Never commit `.env` file
- Use secrets management in production (AWS Secrets Manager, etc.)
- Set appropriate CORS origins for your frontend

### Performance Optimization

- Use a production WSGI server (gunicorn)
- Enable caching for embeddings
- Use a proper database (PostgreSQL) instead of SQLite
- Deploy vector store to a dedicated service (Pinecone, Weaviate)
- Add rate limiting and authentication

### Scaling

- Use Redis for session caching
- Deploy with Docker/Kubernetes
- Use async processing for PDF uploads (Celery, RQ)
- Load balance multiple API instances

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Troubleshooting

### PDF Parsing Issues
- Ensure PDF is text-based (not scanned images)
- Check file size is under 50MB
- Try different PDF parsing libraries if issues persist

### LLM API Errors
- Verify OpenAI API key is valid
- Check API rate limits
- Monitor token usage

### Vector Store Issues
- Ensure sufficient disk space
- Check embedding dimensions match configuration

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
