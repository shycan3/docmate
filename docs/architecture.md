# DocMate MVP Architecture

## Architecture Summary

The implemented MVP uses a dependency-light local architecture:

- Python backend with standard-library HTTP serving
- Static no-build frontend
- Deterministic analysis pipeline for demo and tests
- PyMuPDF-backed PDF text extraction with safe fallback behavior
- Local SQLite storage for saved analysis history
- Source evidence generation for extracted fields and warning conditions
- Clear extension points for future FastAPI, React, and external LLM providers

This is intentionally narrower than the long-term proposal. The goal of the current architecture is local reliability first.

## System Components

### Frontend

- `frontend/index.html`
  - Single-screen work surface
  - Loads local JavaScript and CSS only
- `frontend/src/app.js`
  - Handles upload, profile entry, sample loading, analysis requests, result rendering, and history interactions
- `frontend/src/styles.css`
  - Presents an operator-style tool UI optimized for scanning and action-taking

Responsibilities:

- Collect document and profile input
- Call backend APIs
- Render eligibility, extraction, warnings, checklist, and action links
- Render source evidence, Markdown export, and the presentation demo flow
- Render saved analysis history and load or delete past analyses
- Compare two saved analyses from local history
- Fall back to sample data when backend access is unavailable

### Backend

- `backend/app/models.py`
  - Core data structures for profile, extraction, eligibility, warnings, checklist, and analysis response
- `backend/app/parser.py`
  - Converts uploaded content into text
  - Extracts text from PDFs through PyMuPDF when available
  - Handles safe PDF fallback behavior
- `backend/app/analyzer.py`
  - Produces structured extraction and warning candidates
  - Coordinates sample provider behavior
- `backend/app/eligibility.py`
  - Applies conservative rule-based eligibility evaluation
- `backend/app/checklist.py`
  - Converts extracted requirements into actionable checklist items
- `backend/app/sample_data.py`
  - Supplies deterministic sample announcement text and expected profile/result data
- `backend/app/storage.py`
  - Stores analysis records in local SQLite
- `backend/app/server.py`
  - Exposes HTTP endpoints, history CRUD routes, and static file serving
- `backend/run.py`
  - Starts the local server

### Tests

- `tests/backend/test_analysis.py`
  - Verifies pipeline behavior and rule outcomes
- `tests/backend/test_server.py`
  - Verifies HTTP routes and payload handling

## Runtime Flow

1. The user opens the frontend from the same server that exposes the API.
2. The frontend requests `GET /api/samples` and `GET /api/sample` for sample workflows or submits `POST /api/analyze`.
3. The backend parses the uploaded content into text.
4. The analyzer extracts structured fields and warning candidates.
5. The eligibility module evaluates the extraction against the profile.
6. The checklist module turns extracted requirements into action items.
7. The backend saves the analysis to SQLite and returns a single structured analysis response to the frontend.
8. The frontend can list, reload, or delete saved analyses through the history endpoints.

Supporting route:

- `GET /health` returns a lightweight status check.

## API Shape

### `GET /health`

Response:

```json
{ "status": "ok" }
```

### `GET /api/sample`

Response includes:

- Sample source text
- Sample profile
- Sample analysis result or enough data to build one deterministically

### `GET /api/samples`

Response includes metadata for the built-in sample announcements.

### `POST /api/analyze`

Request:

- Multipart form data or another dependency-light format carrying:
  - uploaded file content or raw text
  - profile fields

Response:

```json
{
  "extraction": {},
  "eligibility": {},
  "warnings": [],
  "checklist": [],
  "actions": []
}
```

Errors must use a simple JSON shape such as:

```json
{ "detail": "..." }
```

### `GET /api/analyses`

Returns saved analysis records ordered newest first.

### `GET /api/analyses/{id}`

Returns one saved analysis record.

### `DELETE /api/analyses`

Clears all saved local analysis records and returns the number of deleted records.

### `DELETE /api/analyses/{id}`

Deletes one saved analysis record.

## Data Model Overview

### Profile

- `age`
- `grade`
- `region`
- `occupation`
- `income_decile`
- `enrolled`

### DocumentExtraction

- `title`
- `application_period`
- `eligibility_conditions`
- `benefits`
- `required_documents`
- `application_method`
- `application_url`

### EligibilityResult

- `status`
- `reasons`
- `missing_information`

### WarningItem

- `severity`
- `title`
- `evidence`

### ChecklistItem

- `title`
- `description`
- `action_url`
- `done`

### AnalysisResult

- `extraction`
- `eligibility`
- `warnings`
- `evidence`
- `checklist`
- `actions`

## Design Constraints

- Local SQLite persistence only; no external database service
- No external network requirement for tests or demo
- No dependency on FastAPI or React for the base flow
- No file persistence for user uploads

## Extension Path

The architecture keeps explicit upgrade points:

- Replace the standard-library server with FastAPI when dependency freedom is no longer required.
- Replace the no-build frontend with React + TypeScript when a richer component model is needed.
- Add provider adapters for Claude or OpenAI after API key setup is available.
- Add Google Calendar OAuth once the MVP proves user value.

These are planned extensions, not current requirements.
