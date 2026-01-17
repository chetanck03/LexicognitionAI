# Requirements Document

## Introduction

Lexicognition AI is an intelligent Viva Voce Examiner system that ingests research papers (PDFs) and conducts live oral examinations to test a user's understanding. The system must analyze any research paper, generate conceptual questions, conduct an interactive interview, and evaluate user responses with scoring and correctness checking.

## Glossary

- **System**: The AI Viva Voce Examiner application
- **PDF_Parser**: Component responsible for extracting and analyzing text from research papers
- **Question_Generator**: Component that creates conceptual questions from paper content
- **Interviewer**: Component that manages the interactive Q&A session
- **Evaluator**: Component that grades answers and checks correctness
- **User**: The person being examined on their understanding of the research paper
- **Research_Paper**: A PDF document containing academic or technical content
- **Conceptual_Question**: A question testing understanding of concepts, not just factual recall
- **Surprise_PDF**: An unseen research paper provided during final evaluation

## Requirements

### Requirement 1: PDF Upload and Ingestion

**User Story:** As a user, I want to upload a research paper PDF, so that the system can analyze it and prepare questions for my examination.

#### Acceptance Criteria

1. WHEN a user uploads a PDF file, THE System SHALL accept PDF files up to 50MB in size
2. WHEN a PDF is uploaded, THE PDF_Parser SHALL extract all text content from the document
3. WHEN text extraction completes, THE System SHALL confirm successful ingestion to the user
4. IF a PDF cannot be parsed, THEN THE System SHALL return a descriptive error message
5. WHEN processing a PDF, THE System SHALL handle multi-column layouts and preserve semantic structure

### Requirement 2: Question Generation

**User Story:** As a user, I want the system to generate exactly 5 conceptual questions from the research paper, so that I can be examined on my understanding.

#### Acceptance Criteria

1. WHEN a research paper is ingested, THE Question_Generator SHALL produce exactly 5 questions
2. THE Question_Generator SHALL create questions that test conceptual understanding rather than factual recall
3. THE Question_Generator SHALL generate questions specific to the content of the uploaded paper
4. THE Question_Generator SHALL include "Why" or "How" questions to test depth of understanding
5. WHEN generating questions, THE Question_Generator SHALL avoid generic questions like "What is the title?"
6. THE Question_Generator SHALL complete question generation within 60 seconds of PDF ingestion

### Requirement 3: Interactive Interview Conduct

**User Story:** As a user, I want to answer questions one at a time in an interactive session, so that I can demonstrate my understanding of the research paper.

#### Acceptance Criteria

1. WHEN the interview begins, THE Interviewer SHALL present questions one at a time
2. THE Interviewer SHALL wait for the user's complete answer before proceeding
3. THE Interviewer SHALL accept both typed text and voice input as answers
4. WHEN a user submits an answer, THE Interviewer SHALL not proceed to the next question until evaluation is complete
5. THE Interviewer SHALL display the current question number and total questions remaining

### Requirement 4: Answer Evaluation and Scoring

**User Story:** As a user, I want my answers to be evaluated with a score and correctness feedback, so that I understand how well I answered each question.

#### Acceptance Criteria

1. WHEN a user submits an answer, THE Evaluator SHALL assign a score from 1 to 10
2. THE Evaluator SHALL determine whether the answer is correct, partially correct, or incorrect
3. WHEN an answer is incorrect, THE Evaluator SHALL identify factual errors or misconceptions
4. THE Evaluator SHALL complete evaluation within 10 seconds of answer submission
5. WHEN evaluation is complete, THE System SHALL display the score and correctness feedback before moving to the next question
6. THE Evaluator SHALL base correctness on the content of the uploaded research paper

### Requirement 5: Fact-Checking and Error Detection

**User Story:** As an examiner, I want the system to detect when a user provides factually incorrect information, so that the evaluation is accurate and educational.

#### Acceptance Criteria

1. WHEN a user provides an answer containing factual errors, THE Evaluator SHALL identify those errors
2. THE Evaluator SHALL compare user answers against the content of the research paper
3. WHEN detecting an error, THE Evaluator SHALL specify which part of the answer is incorrect
4. THE Evaluator SHALL distinguish between incomplete answers and incorrect answers
5. THE Evaluator SHALL handle intentionally wrong answers provided during testing

### Requirement 6: Generalization to Unseen Papers

**User Story:** As a competition participant, I want my system to work with any research paper, so that it can handle the surprise PDF in the finals.

#### Acceptance Criteria

1. THE System SHALL process any research paper PDF without paper-specific hardcoding
2. WHEN given a new research paper, THE Question_Generator SHALL generate relevant questions specific to that paper's content
3. THE System SHALL not rely on pre-trained knowledge specific to particular papers
4. THE System SHALL extract domain-specific terminology and concepts from the uploaded paper
5. WHEN processing papers from different domains, THE System SHALL adapt question complexity appropriately

### Requirement 7: User Interface and Experience

**User Story:** As a user, I want a clear and intuitive chat interface, so that I can focus on answering questions rather than navigating the system.

#### Acceptance Criteria

1. THE System SHALL provide a chat-based interface for the interview
2. WHEN displaying questions, THE System SHALL format them clearly with proper spacing
3. THE System SHALL show the user's previous answers and scores during the session
4. WHEN the interview completes, THE System SHALL display a summary with total score and performance breakdown
5. THE System SHALL provide visual feedback during processing (e.g., "Analyzing paper...", "Evaluating answer...")

### Requirement 8: Voice Input Support

**User Story:** As a user, I want to answer questions using voice input, so that I can simulate a real oral examination experience.

#### Acceptance Criteria

1. WHERE voice input is enabled, THE System SHALL accept spoken answers
2. WHEN voice input is received, THE System SHALL transcribe speech to text accurately
3. THE System SHALL handle common speech patterns and filler words appropriately
4. IF transcription fails, THEN THE System SHALL prompt the user to repeat or type their answer
5. THE System SHALL support both voice and text input modes interchangeably

### Requirement 9: Session Management

**User Story:** As a user, I want my examination session to be tracked and saved, so that I can review my performance later.

#### Acceptance Criteria

1. WHEN an interview begins, THE System SHALL create a unique session identifier
2. THE System SHALL store all questions, answers, and scores for each session
3. WHEN a session completes, THE System SHALL persist the results
4. THE System SHALL allow users to view their past examination sessions
5. IF a session is interrupted, THEN THE System SHALL allow resumption from the last answered question

### Requirement 10: Performance and Reliability

**User Story:** As a competition participant, I want the system to perform reliably during live demonstrations, so that technical issues don't affect my evaluation.

#### Acceptance Criteria

1. THE System SHALL process PDF uploads within 30 seconds for papers up to 20 pages
2. THE System SHALL maintain responsiveness during question generation and evaluation
3. WHEN errors occur, THE System SHALL log them for debugging without crashing
4. THE System SHALL handle concurrent sessions if multiple users access it simultaneously
5. THE System SHALL validate all inputs to prevent injection attacks or malformed data
