# Design Document: AI Viva Voce Examiner

## Overview

The AI Viva Voce Examiner is a sophisticated system that transforms research papers into interactive oral examinations. The system leverages Large Language Models (LLMs) for natural language understanding, Retrieval-Augmented Generation (RAG) for context-aware question generation, and real-time evaluation capabilities to simulate a genuine viva voce experience.

The architecture follows a pipeline approach: PDF ingestion → content analysis → question generation → interactive interview → answer evaluation. Each stage is designed to be modular and testable, with clear interfaces between components.

## Architecture

The system follows a modular, pipeline-based architecture with five core components:

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   PDF       │────▶│   Content    │────▶│   Question     │
│   Parser    │     │   Analyzer   │     │   Generator    │
└─────────────┘     └──────────────┘     └────────────────┘
                                                   │
                                                   ▼
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Session   │◀────│  Interview   │◀────│   Questions    │
│   Manager   │     │  Controller  │     │   (5 items)    │
└─────────────┘     └──────────────┘     └────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Answer     │
                    │   Evaluator  │
                    └──────────────┘
```

### Component Responsibilities

1. **PDF Parser**: Extracts text from PDF files, handling multi-column layouts and preserving structure
2. **Content Analyzer**: Processes extracted text using RAG to identify key concepts, terminology, and relationships
3. **Question Generator**: Creates 5 conceptual questions using LLM with paper context
4. **Interview Controller**: Manages the interactive Q&A flow, one question at a time
5. **Answer Evaluator**: Scores answers (1-10) and checks correctness against paper content
6. **Session Manager**: Tracks examination sessions, stores results, and manages state

## Components and Interfaces

### PDF Parser

**Purpose**: Extract and preprocess text from research paper PDFs.

**Interface**:
```typescript
interface PDFParser {
  parse(file: File): Promise<ParsedDocument>
  validatePDF(file: File): boolean
}

interface ParsedDocument {
  text: string
  metadata: {
    title: string
    authors: string[]
    pageCount: number
  }
  sections: Section[]
}

interface Section {
  heading: string
  content: string
  pageNumber: number
}
```

**Implementation Approach**:
- Use PDF.js or PyPDF2 for text extraction
- Apply heuristics to detect section boundaries
- Preserve paragraph structure and handle multi-column layouts
- Extract metadata from first page

### Content Analyzer (RAG Component)

**Purpose**: Build a searchable knowledge base from the paper for context-aware operations.

**Interface**:
```typescript
interface ContentAnalyzer {
  analyze(document: ParsedDocument): Promise<KnowledgeBase>
  query(kb: KnowledgeBase, query: string): Promise<RelevantChunks>
}

interface KnowledgeBase {
  embeddings: Vector[]
  chunks: TextChunk[]
  concepts: Concept[]
  vectorStore: VectorStore
}

interface TextChunk {
  id: string
  text: string
  embedding: Vector
  section: string
}

interface Concept {
  term: string
  definition: string
  context: string[]
}
```

**Implementation Approach**:
- Chunk document into semantic units (paragraphs or 512-token windows)
- Generate embeddings using OpenAI/Cohere/local model
- Store in vector database (Pinecone, Chroma, or FAISS)
- Extract key concepts using NER or LLM-based extraction
- Build concept graph for relationship tracking

### Question Generator

**Purpose**: Generate 5 conceptual questions that test deep understanding.

**Interface**:
```typescript
interface QuestionGenerator {
  generate(kb: KnowledgeBase): Promise<Question[]>
}

interface Question {
  id: string
  text: string
  type: QuestionType
  expectedConcepts: string[]
  relevantChunks: string[]
  difficulty: number
}

enum QuestionType {
  WHY = "why",
  HOW = "how",
  EXPLAIN = "explain",
  COMPARE = "compare",
  APPLY = "apply"
}
```

**Implementation Approach**:
- Use LLM with carefully crafted prompt including paper context
- Prompt engineering to ensure conceptual (not factual) questions
- Enforce question diversity (different types and topics)
- Retrieve relevant chunks from vector store for each question
- Validate questions are paper-specific (not generic)

**Prompt Strategy**:
```
You are an expert examiner conducting a viva voce examination.
Given this research paper: [PAPER_CONTEXT]

Generate exactly 5 conceptual questions that:
1. Test deep understanding (Why/How questions preferred)
2. Are specific to this paper's content
3. Cannot be answered without reading the paper
4. Cover different aspects of the paper
5. Range from moderate to challenging difficulty

Avoid generic questions like "What is the title?" or "Who are the authors?"
```

### Interview Controller

**Purpose**: Manage the interactive examination flow.

**Interface**:
```typescript
interface InterviewController {
  startInterview(questions: Question[]): Session
  submitAnswer(sessionId: string, answer: string): Promise<EvaluationResult>
  getCurrentQuestion(sessionId: string): Question | null
  getSessionStatus(sessionId: string): SessionStatus
}

interface Session {
  id: string
  questions: Question[]
  currentQuestionIndex: number
  answers: AnswerRecord[]
  status: SessionStatus
}

interface AnswerRecord {
  questionId: string
  answer: string
  score: number
  feedback: string
  timestamp: Date
}

enum SessionStatus {
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  PAUSED = "paused"
}
```

**Implementation Approach**:
- Maintain session state in memory or database
- Present questions sequentially
- Block progression until answer is evaluated
- Support both text and voice input (transcribe voice to text)
- Track timing and user interactions

### Answer Evaluator

**Purpose**: Score answers and check correctness against paper content.

**Interface**:
```typescript
interface AnswerEvaluator {
  evaluate(question: Question, answer: string, kb: KnowledgeBase): Promise<EvaluationResult>
}

interface EvaluationResult {
  score: number // 1-10
  correctness: Correctness
  feedback: string
  factualErrors: string[]
  missingConcepts: string[]
}

enum Correctness {
  CORRECT = "correct",
  PARTIALLY_CORRECT = "partially_correct",
  INCORRECT = "incorrect"
}
```

**Implementation Approach**:
- Use LLM with question, answer, and relevant paper chunks as context
- Retrieve relevant chunks from vector store for fact-checking
- Compare answer against paper content for factual accuracy
- Identify missing key concepts from expected concepts list
- Generate constructive feedback
- Assign score based on: accuracy (40%), completeness (30%), depth (30%)

**Evaluation Prompt Strategy**:
```
You are evaluating a student's answer to a viva voce question.

Question: [QUESTION]
Student Answer: [ANSWER]
Paper Context: [RELEVANT_CHUNKS]
Expected Concepts: [CONCEPTS]

Evaluate the answer on:
1. Factual accuracy (does it contradict the paper?)
2. Completeness (does it cover key concepts?)
3. Depth of understanding (superficial vs. deep)

Provide:
- Score (1-10)
- Correctness (correct/partially_correct/incorrect)
- Specific feedback
- List any factual errors
- List any missing key concepts
```

### Session Manager

**Purpose**: Persist and retrieve examination sessions.

**Interface**:
```typescript
interface SessionManager {
  createSession(userId: string, paperId: string): Session
  saveSession(session: Session): Promise<void>
  getSession(sessionId: string): Promise<Session>
  listUserSessions(userId: string): Promise<SessionSummary[]>
}

interface SessionSummary {
  sessionId: string
  paperTitle: string
  totalScore: number
  completedAt: Date
}
```

**Implementation Approach**:
- Store sessions in database (PostgreSQL, MongoDB, or SQLite)
- Serialize session state including questions, answers, and scores
- Support session resumption for interrupted exams
- Generate summary statistics for completed sessions

## Data Models

### Core Entities

```typescript
// Paper representation
interface Paper {
  id: string
  title: string
  authors: string[]
  uploadedAt: Date
  filePath: string
  parsedDocument: ParsedDocument
  knowledgeBase: KnowledgeBase
}

// User representation
interface User {
  id: string
  name: string
  email: string
  sessions: string[] // session IDs
}

// Complete session with all data
interface ExaminationSession {
  id: string
  userId: string
  paperId: string
  questions: Question[]
  answers: AnswerRecord[]
  status: SessionStatus
  startedAt: Date
  completedAt?: Date
  totalScore: number
  averageScore: number
}
```

### Vector Store Schema

```typescript
interface VectorStoreEntry {
  id: string
  paperId: string
  chunkText: string
  embedding: number[] // 1536-dim for OpenAI, 768-dim for sentence-transformers
  metadata: {
    section: string
    pageNumber: number
    chunkIndex: number
  }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: PDF Size Validation

*For any* file upload attempt, files under 50MB should be accepted and files over 50MB should be rejected with an error.

**Validates: Requirements 1.1**

### Property 2: Text Extraction from Valid PDFs

*For any* valid PDF file with content, the extracted text should be non-empty.

**Validates: Requirements 1.2**

### Property 3: Ingestion Confirmation

*For any* successful PDF parsing, the system should return a confirmation message.

**Validates: Requirements 1.3**

### Property 4: Error Handling for Invalid PDFs

*For any* corrupted or invalid PDF file, the system should return a descriptive error message without crashing.

**Validates: Requirements 1.4**

### Property 5: Exactly Five Questions Generated

*For any* research paper, the question generator should produce exactly 5 questions.

**Validates: Requirements 2.1**

### Property 6: Paper-Specific Question Content

*For any* research paper, the generated questions should contain terminology or concepts that appear in the paper's text.

**Validates: Requirements 2.3**

### Property 7: Depth Questions Included

*For any* set of generated questions, at least one question should contain "Why" or "How" interrogatives.

**Validates: Requirements 2.4**

### Property 8: No Generic Questions

*For any* set of generated questions, none should match generic patterns like "What is the title?" or "Who are the authors?".

**Validates: Requirements 2.5**

### Property 9: Sequential Question Presentation

*For any* active interview session, only one question should be marked as current at any given time.

**Validates: Requirements 3.1**

### Property 10: Answer Required Before Progression

*For any* interview session, the current question index should not increment until an answer is submitted and evaluated.

**Validates: Requirements 3.2, 3.4**

### Property 11: Multiple Input Modalities Accepted

*For any* answer submission, both text and voice input types should be accepted and processed.

**Validates: Requirements 3.3**

### Property 12: Question Progress Tracking

*For any* interview session, the session state should include the current question index and total question count.

**Validates: Requirements 3.5**

### Property 13: Score Range Validation

*For any* answer evaluation, the assigned score should be between 1 and 10 inclusive.

**Validates: Requirements 4.1**

### Property 14: Correctness Classification

*For any* answer evaluation, the correctness value should be one of: correct, partially_correct, or incorrect.

**Validates: Requirements 4.2**

### Property 15: Error Identification for Incorrect Answers

*For any* evaluation where correctness is "incorrect", the feedback should contain identification of specific errors or misconceptions.

**Validates: Requirements 4.3, 5.3**

### Property 16: Evaluation Before Progression

*For any* interview session, evaluation results (score and feedback) should be available before the question index advances.

**Validates: Requirements 4.5**

### Property 17: Robust Error Handling

*For any* intentionally incorrect answer, the system should produce a valid evaluation without crashing.

**Validates: Requirements 5.5**

### Property 18: Paper-Specific Question Differentiation

*For any* two different research papers, the generated questions should be distinct and contain different paper-specific terminology.

**Validates: Requirements 6.2**

### Property 19: Concept Extraction from Paper

*For any* research paper, the knowledge base should contain extracted concepts that appear in the paper's text.

**Validates: Requirements 6.4**

### Property 20: Session History Tracking

*For any* interview session with submitted answers, the session state should include all previous answers and their scores.

**Validates: Requirements 7.3**

### Property 21: Session Summary Generation

*For any* completed interview session, a summary with total score and performance breakdown should be generated.

**Validates: Requirements 7.4**

### Property 22: Voice Input Processing

*For any* session where voice input is enabled, spoken answers should be transcribed and processed as text.

**Validates: Requirements 8.1**

### Property 23: Transcription Error Handling

*For any* transcription failure, the system should prompt for retry or alternative input without crashing.

**Validates: Requirements 8.4**

### Property 24: Input Mode Flexibility

*For any* interview session, users should be able to switch between voice and text input modes.

**Validates: Requirements 8.5**

### Property 25: Unique Session Identifiers

*For any* newly created interview session, the session ID should be unique and non-empty.

**Validates: Requirements 9.1**

### Property 26: Session Data Persistence

*For any* interview session, all questions, answers, and scores should be stored and retrievable after completion.

**Validates: Requirements 9.2, 9.3**

### Property 27: Session Retrieval by User

*For any* user with completed sessions, those sessions should be retrievable by user ID.

**Validates: Requirements 9.4**

### Property 28: Session Resumption

*For any* interrupted session, resuming should continue from the last answered question with all previous data intact.

**Validates: Requirements 9.5**

### Property 29: Error Logging Without Crashes

*For any* error condition during operation, the error should be logged and the system should continue functioning.

**Validates: Requirements 10.3**

### Property 30: Concurrent Session Isolation

*For any* two concurrent sessions, operations in one session should not affect the state of the other session.

**Validates: Requirements 10.4**

### Property 31: Input Validation

*For any* user input, malformed or potentially malicious data should be rejected with appropriate error messages.

**Validates: Requirements 10.5**

## Error Handling

### Error Categories

1. **Input Errors**
   - Invalid PDF format
   - File size exceeded
   - Corrupted file data
   - Malformed user input

2. **Processing Errors**
   - PDF parsing failures
   - Embedding generation failures
   - LLM API errors (rate limits, timeouts)
   - Vector store connection issues

3. **State Errors**
   - Invalid session ID
   - Session already completed
   - Missing required data

4. **External Service Errors**
   - LLM API unavailable
   - Vector database unavailable
   - Speech-to-text service failures

### Error Handling Strategy

**Graceful Degradation**:
- If vector store fails, fall back to keyword-based retrieval
- If LLM API fails, retry with exponential backoff (3 attempts)
- If speech-to-text fails, prompt user to type answer

**User-Friendly Messages**:
- Never expose internal error details to users
- Provide actionable guidance ("Please try a smaller PDF" vs "Memory allocation failed")
- Log detailed errors for debugging

**Error Recovery**:
- Save session state before each operation
- Allow session resumption after failures
- Implement transaction-like behavior for critical operations

**Validation**:
- Validate all inputs at API boundaries
- Sanitize user text to prevent injection
- Check file types and sizes before processing

## Testing Strategy

### Dual Testing Approach

This system requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of correct behavior
- Edge cases (empty PDFs, single-page papers, maximum size files)
- Error conditions (corrupted PDFs, invalid inputs)
- Integration points between components
- Mock external services (LLM APIs, vector stores)

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must be maintained
- Round-trip properties (serialization/deserialization)

### Property-Based Testing Configuration

**Framework**: Use `fast-check` for TypeScript/JavaScript or `Hypothesis` for Python

**Test Configuration**:
- Minimum 100 iterations per property test
- Each test must reference its design document property
- Tag format: `Feature: ai-viva-examiner, Property {number}: {property_text}`

**Example Property Test Structure**:
```typescript
// Feature: ai-viva-examiner, Property 5: Exactly Five Questions Generated
test('question generator produces exactly 5 questions', async () => {
  await fc.assert(
    fc.asyncProperty(
      arbitraryPaper(), // generates random paper content
      async (paper) => {
        const questions = await questionGenerator.generate(paper);
        expect(questions).toHaveLength(5);
      }
    ),
    { numRuns: 100 }
  );
});
```

### Test Data Generators

**For Property Tests**:
- `arbitraryPaper()`: Generate random research papers with varying lengths, structures
- `arbitraryAnswer()`: Generate random user answers (correct, incorrect, incomplete)
- `arbitraryPDFFile()`: Generate valid and invalid PDF files
- `arbitrarySession()`: Generate sessions in various states

**For Unit Tests**:
- Use real research papers (e.g., "Attention Is All You Need")
- Create fixture PDFs with known content
- Prepare example answers with known correctness

### Integration Testing

**End-to-End Flow**:
1. Upload a known PDF
2. Verify 5 questions are generated
3. Submit answers (mix of correct and incorrect)
4. Verify scores and feedback
5. Check session persistence

**External Service Mocking**:
- Mock LLM API responses for consistent testing
- Mock vector store for deterministic retrieval
- Mock speech-to-text for voice input tests

### Performance Testing

While not part of property-based testing, monitor:
- PDF processing time (should be < 30s for 20-page papers)
- Question generation time (should be < 60s)
- Answer evaluation time (should be < 10s)
- Concurrent session handling (test with 10+ simultaneous users)

### Testing Priorities

**Critical Path** (must have 100% coverage):
1. PDF parsing and text extraction
2. Question generation (exactly 5, paper-specific)
3. Answer evaluation (scoring, correctness)
4. Session state management

**Important** (should have high coverage):
1. Error handling for all failure modes
2. Input validation
3. Session persistence and retrieval

**Nice to Have**:
1. Voice input transcription
2. UI formatting and display
3. Performance optimizations

## Implementation Notes

### Technology Stack Recommendations

**Backend**:
- Python with FastAPI or Node.js with Express
- LangChain for RAG pipeline orchestration
- OpenAI API or Anthropic Claude for LLM
- Pinecone, Chroma, or FAISS for vector storage
- PostgreSQL or MongoDB for session storage

**PDF Processing**:
- PyPDF2 or pdfplumber (Python)
- PDF.js (JavaScript)

**Speech-to-Text** (optional):
- OpenAI Whisper API
- Google Cloud Speech-to-Text
- Web Speech API (browser-based)

**Frontend**:
- React or Vue.js for chat interface
- TailwindCSS for styling
- WebSocket for real-time updates

### Deployment Considerations

**For Competition Demo**:
- Ensure all dependencies are installed and tested
- Have fallback for API failures (cached responses)
- Test with the "Attention Is All You Need" paper thoroughly
- Prepare for quick PDF ingestion (< 30s)
- Have clear error messages for judges

**Scalability** (if needed later):
- Cache embeddings for frequently used papers
- Use async processing for PDF ingestion
- Implement rate limiting for API calls
- Consider serverless deployment (AWS Lambda, Vercel)

### Key Design Decisions

1. **RAG over Fine-tuning**: Using RAG allows the system to work with any paper without retraining
2. **Sequential Interview**: One question at a time ensures focused evaluation and better UX
3. **LLM-based Evaluation**: Provides nuanced scoring and feedback compared to keyword matching
4. **Modular Architecture**: Each component can be tested and improved independently
5. **Session Persistence**: Allows resumption and historical analysis

### Risks and Mitigations

**Risk**: LLM generates generic questions
**Mitigation**: Careful prompt engineering, validation against paper content, multiple generation attempts

**Risk**: Evaluation is inconsistent or unfair
**Mitigation**: Use paper context in evaluation, test with known correct/incorrect answers, allow score calibration

**Risk**: PDF parsing fails on complex layouts
**Mitigation**: Test with diverse PDFs, have manual text input fallback, use robust parsing libraries

**Risk**: System is too slow for live demo
**Mitigation**: Optimize embedding generation, cache results, use faster LLM models, pre-process test papers
