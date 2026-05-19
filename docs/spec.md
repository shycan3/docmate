# DocMate MVP Spec

## Product Goal

DocMate turns scholarship and youth-policy announcement documents into action-ready guidance.
The MVP must help a user move from "I found a document" to "I know whether I can apply and what to do next" without requiring an API key or external service setup.

Core outcomes:

- Extract the key application details from an uploaded document.
- Compare those details against a user profile and return a conservative 3-state eligibility result.
- Surface warnings that commonly cause failed applications.
- Convert requirements into a concrete checklist with direct action links.
- Provide immediate next actions such as opening the application page and adding a deadline to a calendar flow.

## MVP Scope

### Supported Inputs

- Text-based PDF documents, primarily 1 to 5 pages.
- Plain text uploads or decodable file content for local testing and fallback flows.
- Scholarship and youth-policy announcements for university students and young adults.

### Supported User Profile Fields

- Age
- Grade
- Region
- Occupation
- Income decile
- Enrollment status

### Supported Outputs

- Structured summary of the announcement:
  - Title
  - Application period
  - Eligibility conditions
  - Benefits
  - Required documents
  - Application method
  - Application URL
- Eligibility result:
  - `eligible`
  - `needs_review`
  - `ineligible`
- Warning items for risky conditions such as:
  - Duplicate application restrictions
  - No-edit policies
  - Automatic rejection conditions
  - Missing-document rejection
  - Nationality restrictions
- Actionable checklist items with optional related URLs.
- Immediate actions for opening the application page and registering the deadline.
- Local analysis history for previously analyzed documents.
- Source evidence snippets that connect extracted fields and warnings back to the original text.
- Side-by-side comparison for two saved analysis results.
- Markdown export for the current analysis result.
- Presentation demo mode for built-in samples.

## Primary User Flow

1. The user uploads a document or chooses a built-in sample announcement.
2. The user enters profile information.
3. The system extracts document text.
4. The system analyzes the text into a structured extraction.
5. The system evaluates eligibility against the profile.
6. The system highlights warnings and generates a checklist.
7. The user follows the provided action links.

## Functional Requirements

### Document Analysis

- The system must accept uploaded file content without permanently storing the original file on disk.
- The system must extract text from decodable inputs directly.
- The system must handle PDFs safely even when a PDF parsing library is unavailable.
- The system must preserve a deterministic sample flow so the MVP demo works without external dependencies.

### Eligibility Evaluation

- The system must use rule-based checks for simple conditions such as age, region, and enrollment.
- The system must return `needs_review` when profile data is missing or the condition cannot be interpreted confidently.
- The system must avoid optimistic guesses for complex nested conditions.

### Warning Detection

- The system must detect and surface critical risk language when present in the source text.
- The warning list must prioritize issues that can cause submission failure or disqualification.

### Evidence Display

- The system must return concise source snippets for extracted fields and detected warnings.
- Evidence snippets should be short enough for a result card and should preserve the original wording where possible.
- The UI must show evidence near the analysis result so users can verify the basis for the recommendation.

### Checklist Generation

- The system must convert required documents and application steps into action-oriented checklist items.
- Checklist items should use imperative phrasing so the user can act immediately.

### Demo Reliability

- The MVP must return a consistent sample analysis result without requiring:
  - API keys
  - OAuth setup
  - database provisioning
  - external network access

### Local History

- The system must save completed analysis results to a local SQLite database.
- The system must expose endpoints to list, retrieve, and delete saved analyses.
- Saved history must not require login, cloud storage, or external database setup.
- The system must not persist uploaded original files; only extracted text, profile input, and analysis output are stored.
- Users must be able to compare two saved analyses side by side.

## Non-Goals

The MVP explicitly excludes:

- Login, subscription, billing, or account management
- Multi-user cloud synchronization
- Real Google OAuth write access
- Automatic document issuance from government or school portals
- Image-heavy PDFs and OCR-first pipelines
- Legal or contract documents with dense nested exceptions
- Full automation for complex eligibility rules

## Implementation Constraints

- The local MVP must be dependency-light and runnable in restricted environments.
- The backend must work with the Python standard library only for the core demo path.
- The frontend must render without npm install or external CDN assets.
- Real LLM providers and richer frameworks remain extension points, not MVP requirements.

## Definition Of Done For The MVP

- A user can complete the sample analysis flow end to end on a local machine without network access.
- Structured extraction, eligibility, warnings, checklist, and action links are all visible in the product flow.
- The implementation remains aligned with the future path toward FastAPI, React, and real LLM providers, but does not depend on them now.
