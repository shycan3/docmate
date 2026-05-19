# DocMate

DocMate turns scholarship and youth-policy announcements into action-ready guidance. The current build runs locally with a Python backend, no-build frontend, PyMuPDF PDF extraction, and SQLite history.

## What It Does

- Extracts application period, eligibility conditions, benefits, required documents, method, and URL.
- Compares the announcement with a user profile and returns `eligible`, `needs_review`, or `ineligible`.
- Highlights risk conditions such as duplicate support restrictions, no-edit rules, missing-document rejection, and automatic disqualification.
- Shows source evidence snippets so users can see why a result was produced.
- Builds an actionable checklist with direct links.
- Saves analysis results locally and lets the user reload or delete them from the history tab.
- Compares two saved notices side by side from the history tab.
- Runs a presentation demo mode that analyzes all three built-in samples and opens the comparison view.
- Exports the current result as a Markdown checklist.
- Provides application and Google Calendar deadline links when the document contains enough information.

## Install

```bash
python -m pip install -r requirements.txt
```

The only required third-party package is `PyMuPDF`, used for real PDF text extraction. Text uploads, built-in samples, tests, and the fallback parser still avoid API keys and external services.

## Run

```bash
python backend/run.py
```

Open:

```text
http://127.0.0.1:8000
```

The same server provides the UI and API.

## API

```text
GET    /health
GET    /api/samples
GET    /api/sample
POST   /api/analyze
GET    /api/analyses
GET    /api/analyses/{id}
DELETE /api/analyses
DELETE /api/analyses/{id}
```

`POST /api/analyze` accepts JSON:

```json
{
  "filename": "notice.txt",
  "text": "신청 기간: 2026-05-01 ~ 2026-05-31",
  "profile": {
    "age": 22,
    "grade": "3학년",
    "region": "서울",
    "occupation": "대학생",
    "income_decile": 5,
    "enrolled": true
  }
}
```

It also accepts multipart form data with `file` and `profile`. Use `use_sample=true` and `sample_id` to analyze a built-in sample.

## Samples

The app includes three demo notices:

- `seoul-hope-scholarship`: youth scholarship with age, region, enrollment, and income rules.
- `graduate-talent-scholarship`: graduate scholarship with document and no-edit risks.
- `busan-youth-living-fund`: youth-policy fund with strict income and job-seeker conditions.

## Presentation Flow

For a fast demo:

1. Start the server and open `http://127.0.0.1:8000`.
2. Click `데모 기록 초기화` if you want a clean rehearsal.
3. Click `데모 모드 실행`.
4. The app analyzes all three samples, saves them, and opens the history comparison panel.
5. Open one saved result to show eligibility, source evidence, warnings, checklist, and Markdown export.

Latest presentation screenshots are stored under `tasks/0-docmate-mvp/artifacts/`.

Presentation review notes:

- Persona feedback: `docs/persona-feedback.md`
- Judge feedback: `docs/judge-feedback.md`
- Demo script: `docs/demo-script.md`

## Verify

```bash
python -m compileall backend scripts
python -m unittest discover -s tests -p "test_*.py" -t .
node --check frontend/src/app.js
python scripts/check_smoke.py
```

The `-t .` flag keeps Python test discovery anchored at the repository root so `tests/backend` does not shadow the application package.

## Project Shape

```text
backend/        local API, parser, analysis pipeline, SQLite storage
frontend/       no-build browser UI with analysis and history tabs
docs/           product spec, architecture, ADR, business model, user notes
tests/          unittest coverage
tasks/          harness artifacts and phase history
```

## Roadmap

Remaining development work is tracked in `docs/roadmap.md`. The current service is presentation-ready as a local competition demo, while public beta and production launch still require deployment, account isolation, privacy policy work, real-document fixtures, CI, and operational hardening.

## MVP Boundaries

Implemented now:

- PyMuPDF text extraction for text-based PDFs.
- Local SQLite history via `docmate.db`.
- Three built-in samples for demos.
- Rule-based eligibility and deterministic fallback analysis.

Still future work:

- FastAPI and React migration.
- Claude/OpenAI provider adapters.
- Google OAuth calendar write access.
- OCR for image-heavy PDFs.
- Cloud accounts and multi-user sync.

## Troubleshooting

- If the browser says a page failed to load, verify `python backend/run.py` is running and that port `8000` is free.
- If `http://127.0.0.1:8000/api/analyses` opens in the browser, you should expect JSON such as `{ "analyses": [] }`.
- Use `http://127.0.0.1:8000/health` for a quick server check.
