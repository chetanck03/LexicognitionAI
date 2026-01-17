# Implementation Plan: AI Viva Voce Examiner

## Overview

This implementation plan breaks down the AI Viva Voce Examiner into discrete, testable tasks. The approach follows a bottom-up strategy: build core components first (PDF parsing, RAG pipeline), then question generation and evaluation, and finally wire everything together with the interview controller and session management. We'll use Python for implementation given its strong ecosystem for AI/ML tasks (LangChain, OpenAI, vector databases).

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create Python project with virtual environment
  - Install core dependencies: FastAPI, LangChain, OpenAI SDK, PyPDF2, Pydantic
  - Install vector store library (FAISS or Chroma for local development)
  - Set up testing framework (pytest, hypothesis for property-based testing)
  - Create directory structure: `src/`, `tests/`, `data/`
  - _Requirements: 10.5_

- [ ] 2. Implement PDF Parser component
  - [ ] 2.1 Create PDF parser with text extraction
    - Implement `PDFParser` class with `parse()` method
    - Extract text using PyPDF2 or pdfplumber
    - Handle multi-column layouts and preserve structure
    - Extract metadata (title, authors, page count)
    - Implement section detection heuristics
    - _Requirements: 1.2, 1.5_

  - [ ]* 2.2 Write property test for PDF parser
    - **Property 2: Text Extraction from Valid PDFs**
    - **Validates: Requirements 1.2**

  - [ ] 2.3 Implement file validation
    - Check file size (max 50MB)
    - Validate PDF format
    - Return descriptive errors for invalid files
    - _Requirements: 1.1, 1.4_

  - [ ]* 2.4 Write property tests for file validation
    - **Property 1: PDF Size Validation**
    - **Property 4: Error Handling for Invalid PDFs**
    - **Validates: Requirements 1.1, 1.4**

  - [ ]* 2.5 Write unit tests for PDF parser
    - Test with sample PDFs (single-page, multi-page, multi-column)
    - Test error cases (corrupted files, non-PDF files)
    - _Requirements: 1.1, 1.2, 1.4_

- [ ] 3. Implement Content Analyzer (RAG component)
  - [ ] 3.1 Create text chunking functionality
    - Implement semantic chunking (512-token windows with overlap)
    - Preserve section context in chunks
    - Create `TextChunk` data model
    - _Requirements: 6.4_

  - [ ] 3.2 Implement embedding generation and vector store
    - Generate embeddings using OpenAI or sentence-transformers
    - Initialize FAISS or Chroma vector store
    - Store chunks with embeddings and metadata
    - Implement similarity search functionality
    - _Requirements: 6.4_

  - [ ] 3.3 Create concept extraction
    - Extract key terms and concepts from paper
    - Build concept list with definitions and context
    - Store in `KnowledgeBase` data model
    - _Requirements: 6.4_

  - [ ]* 3.4 Write property test for concept extraction
    - **Property 19: Concept Extraction from Paper**
    - **Validates: Requirements 6.4**

  - [ ]* 3.5 Write unit tests for content analyzer
    - Test chunking with various text lengths
    - Test embedding generation
    - Test vector store operations (add, search)
    - _Requirements: 6.4_

- [ ] 4. Checkpoint - Verify PDF processing and RAG pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Question Generator
  - [ ] 5.1 Create question generation with LLM
    - Implement `QuestionGenerator` class
    - Design prompt for conceptual question generation
    - Use LangChain to orchestrate LLM calls with paper context
    - Retrieve relevant chunks from vector store for context
    - Generate exactly 5 questions
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 5.2 Implement question validation
    - Check for paper-specific content in questions
    - Ensure at least one "Why" or "How" question
    - Filter out generic questions
    - Validate question diversity (different topics)
    - _Requirements: 2.3, 2.4, 2.5_

  - [ ]* 5.3 Write property tests for question generation
    - **Property 5: Exactly Five Questions Generated**
    - **Property 6: Paper-Specific Question Content**
    - **Property 7: Depth Questions Included**
    - **Property 8: No Generic Questions**
    - **Validates: Requirements 2.1, 2.3, 2.4, 2.5**

  - [ ]* 5.4 Write property test for question differentiation
    - **Property 18: Paper-Specific Question Differentiation**
    - **Validates: Requirements 6.2**

  - [ ]* 5.5 Write unit tests for question generator
    - Test with "Attention Is All You Need" paper
    - Verify questions contain paper-specific terms (e.g., "self-attention", "positional encoding")
    - Test question diversity
    - _Requirements: 2.1, 2.3, 2.4, 2.5_

- [ ] 6. Implement Answer Evaluator
  - [ ] 6.1 Create answer evaluation with LLM
    - Implement `AnswerEvaluator` class with `evaluate()` method
    - Design evaluation prompt with question, answer, and paper context
    - Retrieve relevant chunks for fact-checking
    - Generate score (1-10), correctness, and feedback
    - Identify factual errors and missing concepts
    - _Requirements: 4.1, 4.2, 4.3, 4.6, 5.1, 5.3_

  - [ ]* 6.2 Write property tests for answer evaluation
    - **Property 13: Score Range Validation**
    - **Property 14: Correctness Classification**
    - **Property 15: Error Identification for Incorrect Answers**
    - **Property 17: Robust Error Handling**
    - **Validates: Requirements 4.1, 4.2, 4.3, 5.5**

  - [ ]* 6.3 Write unit tests for answer evaluator
    - Test with known correct answers
    - Test with known incorrect answers (factual errors)
    - Test with incomplete answers
    - Verify score ranges and feedback quality
    - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.4_

- [ ] 7. Checkpoint - Verify question generation and evaluation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Session Manager
  - [ ] 8.1 Create session data models
    - Define `Session`, `AnswerRecord`, `SessionStatus` models using Pydantic
    - Implement session state tracking
    - _Requirements: 9.1, 9.2_

  - [ ] 8.2 Implement session persistence
    - Create `SessionManager` class
    - Implement session storage (SQLite or JSON files for simplicity)
    - Implement session retrieval by ID and user ID
    - Support session resumption for interrupted exams
    - _Requirements: 9.2, 9.3, 9.4, 9.5_

  - [ ]* 8.3 Write property tests for session management
    - **Property 25: Unique Session Identifiers**
    - **Property 26: Session Data Persistence**
    - **Property 27: Session Retrieval by User**
    - **Property 28: Session Resumption**
    - **Property 30: Concurrent Session Isolation**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 10.4**

  - [ ]* 8.4 Write unit tests for session manager
    - Test session creation and storage
    - Test session retrieval
    - Test resumption of interrupted sessions
    - Test concurrent session handling
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 9. Implement Interview Controller
  - [ ] 9.1 Create interview flow management
    - Implement `InterviewController` class
    - Implement `startInterview()` to initialize session with questions
    - Implement `submitAnswer()` to process answers and trigger evaluation
    - Implement `getCurrentQuestion()` to get active question
    - Ensure sequential question presentation (one at a time)
    - Block progression until answer is evaluated
    - _Requirements: 3.1, 3.2, 3.4, 4.5_

  - [ ] 9.2 Implement session status tracking
    - Track current question index
    - Store answer history with scores
    - Update session status (in_progress, completed, paused)
    - Generate session summary on completion
    - _Requirements: 3.5, 7.3, 7.4_

  - [ ]* 9.3 Write property tests for interview controller
    - **Property 9: Sequential Question Presentation**
    - **Property 10: Answer Required Before Progression**
    - **Property 12: Question Progress Tracking**
    - **Property 16: Evaluation Before Progression**
    - **Property 20: Session History Tracking**
    - **Property 21: Session Summary Generation**
    - **Validates: Requirements 3.1, 3.2, 3.4, 3.5, 4.5, 7.3, 7.4**

  - [ ]* 9.4 Write unit tests for interview controller
    - Test complete interview flow
    - Test answer submission and evaluation
    - Test session completion and summary
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 4.5_

- [ ] 10. Implement input handling and validation
  - [ ] 10.1 Create input validation
    - Validate and sanitize all user inputs
    - Implement file upload validation
    - Prevent injection attacks
    - Return appropriate error messages
    - _Requirements: 10.5_

  - [ ] 10.2 Implement voice input support (optional)
    - Integrate speech-to-text API (OpenAI Whisper or Web Speech API)
    - Transcribe voice to text
    - Handle transcription errors with retry prompts
    - Support switching between voice and text input
    - _Requirements: 3.3, 8.1, 8.4, 8.5_

  - [ ]* 10.3 Write property tests for input handling
    - **Property 11: Multiple Input Modalities Accepted**
    - **Property 22: Voice Input Processing**
    - **Property 23: Transcription Error Handling**
    - **Property 24: Input Mode Flexibility**
    - **Property 31: Input Validation**
    - **Validates: Requirements 3.3, 8.1, 8.4, 8.5, 10.5**

  - [ ]* 10.4 Write unit tests for input validation
    - Test malformed inputs
    - Test injection attempts
    - Test voice input transcription (if implemented)
    - _Requirements: 3.3, 10.5_

- [ ] 11. Implement error handling and logging
  - [ ] 11.1 Create error handling infrastructure
    - Implement try-catch blocks for all external calls
    - Log errors without crashing
    - Implement retry logic for LLM API calls
    - Provide user-friendly error messages
    - _Requirements: 10.3_

  - [ ]* 11.2 Write property test for error handling
    - **Property 29: Error Logging Without Crashes**
    - **Validates: Requirements 10.3**

  - [ ]* 11.3 Write unit tests for error handling
    - Test LLM API failures
    - Test vector store failures
    - Test PDF parsing failures
    - Verify graceful degradation
    - _Requirements: 10.3_

- [ ] 12. Checkpoint - Verify complete system integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Create API endpoints with FastAPI
  - [ ] 13.1 Implement REST API endpoints
    - POST `/upload` - Upload PDF and create knowledge base
    - POST `/interview/start` - Start interview with generated questions
    - POST `/interview/answer` - Submit answer and get evaluation
    - GET `/interview/status/:sessionId` - Get current session status
    - GET `/sessions/:userId` - List user's past sessions
    - POST `/interview/resume/:sessionId` - Resume interrupted session
    - _Requirements: 1.1, 1.3, 3.1, 3.2, 9.4, 9.5_

  - [ ] 13.2 Implement request/response models
    - Define Pydantic models for all API requests and responses
    - Add input validation
    - Add error response models
    - _Requirements: 10.5_

  - [ ]* 13.3 Write integration tests for API
    - Test complete flow: upload → start → answer → complete
    - Test error cases
    - Test session resumption
    - _Requirements: 1.1, 3.1, 3.2, 9.5_

- [ ] 14. Create chat-based user interface
  - [ ] 14.1 Build frontend with React or simple HTML/JS
    - Create chat interface for Q&A
    - Display questions one at a time
    - Show answer history and scores
    - Display session summary on completion
    - Add loading indicators during processing
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 14.2 Implement file upload UI
    - Create PDF upload component
    - Show upload progress
    - Display confirmation or error messages
    - _Requirements: 1.1, 1.3, 1.4_

  - [ ]* 14.3 Write UI tests
    - Test file upload flow
    - Test interview interaction
    - Test display of scores and feedback
    - _Requirements: 7.1, 7.3, 7.4_

- [ ] 15. Test with competition papers
  - [ ] 15.1 Test with "Attention Is All You Need" paper
    - Upload the paper and verify processing
    - Review generated questions for quality
    - Test with sample answers
    - Verify evaluation accuracy
    - _Requirements: 2.3, 4.6, 6.2_

  - [ ] 15.2 Test with diverse papers
    - Test with papers from different domains (CV, NLP, Physics)
    - Verify question generation adapts to content
    - Verify no hardcoding for specific papers
    - _Requirements: 6.1, 6.2, 6.5_

  - [ ]* 15.3 Conduct end-to-end testing
    - Simulate judge interaction
    - Test with intentionally wrong answers
    - Verify fact-checking works
    - Measure processing times
    - _Requirements: 5.1, 5.5, 10.1_

- [ ] 16. Final checkpoint and optimization
  - Ensure all tests pass
  - Optimize performance (caching, async processing)
  - Prepare demo environment
  - Document setup and usage instructions
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Focus on getting the core flow working first (PDF → Questions → Evaluation)
- Voice input (task 10.2) is optional and can be added later
- The system must work with any research paper, not just "Attention Is All You Need"
