# DocMate Remaining Development Roadmap

**Updated:** 2026-05-19  
**Baseline:** Public GitHub MVP with local server, PyMuPDF extraction, SQLite history, evidence cards, comparison, demo mode, and Markdown export

## Current Readiness

DocMate is now strong enough for a competition-style local service demo. The core user journey works end to end:

- Upload or select a scholarship/youth-policy notice.
- Enter a user profile.
- Receive structured extraction, eligibility status, warnings, checklist, action links, and evidence snippets.
- Save analyses to local history.
- Compare two saved notices.
- Export the current result as a Markdown checklist.
- Run a repeatable presentation demo with built-in samples.

Estimated readiness by target:

| Target | Estimate | Meaning |
| --- | ---: | --- |
| Competition presentation demo | 90-95% | The service can be shown live and explains its value clearly. |
| Public beta | 55-60% | The workflow is useful, but deployment, auth, privacy, and real-document coverage are not done. |
| Production launch | 40-50% | Core product direction is clear, but reliability, operations, security, and scale features remain. |

These percentages are product-readiness estimates, not test coverage or code-completion metrics.

## Priority Roadmap

### P0: Presentation Hardening

Goal: Make the current local service reliable and convincing for judging.

| Item | Why It Matters | Done When |
| --- | --- | --- |
| Demo script | Keeps the live pitch crisp and repeatable. | `docs/demo-script.md` explains the 3-5 minute flow, expected clicks, and fallback plan. |
| Realistic fixture set | Shows the product can handle more than hand-written samples. | At least 5 representative notices are stored as test fixtures with expected outputs. |
| Screenshot/GIF assets | Helps README and presentation materials communicate fast. | README includes the latest UI screenshot and a short demo asset if available. |
| Demo data reset | Prevents stale local history from confusing the presentation. | A reset command or UI action clears local demo records safely. |
| Error-state polish | Judges may try unsupported files or empty input. | Empty, malformed, and unsupported-file states are clear and recoverable. |

### P1: Public Beta Foundation

Goal: Let real users try DocMate outside the developer's machine.

| Item | Why It Matters | Done When |
| --- | --- | --- |
| Cloud deployment | Users need a stable public URL. | App is deployed behind HTTPS with a documented release process. |
| Account and user history | Local SQLite is not enough for returning users. | Users can sign in and see only their own saved analyses. |
| Privacy and retention policy | Uploaded notices and profile fields are sensitive. | Privacy policy, deletion rules, and upload-retention behavior are documented and implemented. |
| Production database | Multi-user history needs durable storage. | PostgreSQL or equivalent is used with migrations and backups. |
| Real-document evaluation | Parser reliability must be measured. | A fixture suite tracks extraction accuracy across 20-50 real or anonymized notices. |
| LLM provider adapter | Complex wording needs stronger extraction support. | Claude/OpenAI-style providers can be enabled behind a stable interface with citations and fallback behavior. |
| CI workflow | GitHub updates should stay safe as development continues. | Automated tests run on push and pull request. |

### P2: Production Differentiators

Goal: Move from useful beta to a service that can compete and scale.

| Item | Why It Matters | Done When |
| --- | --- | --- |
| OCR support | Many official PDFs are scanned or image-heavy. | Image-heavy PDFs produce usable text or a clear "OCR needed" result. |
| Calendar integration | Reminders are a strong retention feature. | Users can export ICS files or connect Google Calendar through OAuth. |
| Institution workflows | B2B use needs admin-facing controls. | Schools or local governments can manage notice templates, review outputs, or see aggregate usage. |
| Feedback loop | Eligibility mistakes must be corrected quickly. | Users can mark extraction/eligibility issues and the team can review them. |
| Monitoring and audit logs | Production issues need visibility. | Server errors, analysis failures, and slow requests are tracked. |
| Rate limits and cost controls | LLM-backed analysis can become expensive. | Per-user limits, queueing, and provider-cost metrics are enforced. |
| Payment or pilot packaging | The business model needs validation. | Premium or institution pilot terms are testable with real users. |

## Development Backlog By Area

### Data And Accuracy

- Build a fixture library from scholarship, university, local-government, and youth-policy notices.
- Add snapshot tests for extracted title, period, eligibility, benefits, required documents, warnings, and evidence.
- Track false positive and false negative eligibility cases.
- Add confidence metadata for extraction fields when real LLM providers are introduced.
- Keep the default eligibility posture conservative: ambiguous cases should remain `needs_review`.

### Parsing And Files

- Improve table and list extraction for official PDF formats.
- Add OCR for scanned PDFs or explicitly route those files to an OCR-needed state.
- Add upload size limits and user-friendly errors for huge, encrypted, or damaged files.
- Preserve the current rule that original uploads are not permanently stored unless a future privacy policy explicitly permits it.

### Backend And Infrastructure

- Migrate from `http.server` to FastAPI when public deployment begins.
- Add request validation, structured error types, and versioned API responses.
- Replace local-only SQLite with PostgreSQL for multi-user mode.
- Add database migrations and backup/restore procedures.
- Add CI, deployment scripts, logging, monitoring, and rate limits.

### Frontend And Product UX

- Consider React + TypeScript once the UI starts needing reusable components, route state, and richer test coverage.
- Add a guided comparison flow for users deciding between several notices.
- Add accessibility checks for keyboard navigation, focus state, contrast, and screen-reader labels.
- Add mobile QA for small-screen scholarship browsing.
- Add export polish: PDF export, share links, or application-prep bundles.

### Security, Privacy, And Compliance

- Add account isolation before any public multi-user launch.
- Define what profile data is stored, how long it is retained, and how users delete it.
- Avoid storing original uploaded documents by default.
- Add server-side file validation and malware-scan strategy before accepting public uploads.
- Add legal disclaimers that DocMate is an application aid, not the final authority for eligibility.

### Integrations

- Add ICS export before full OAuth if a lower-friction reminder feature is needed.
- Add Google Calendar OAuth only after users prove reminder demand.
- Add institution-specific application and document-issuance link maps.
- Explore integrations with university portals, scholarship platforms, or youth-policy newsletters.

### Business Validation

- Run a 20-50 user study with target students or job-seeking youth.
- Ask each user to analyze at least three real notices.
- Measure time saved, confidence gained, application-link clicks, history reuse, and missed-document prevention.
- Interview university support teams or student councils for B2B pilot interest.
- Validate whether users value reminders, comparison, saved history, or institution-backed workflows enough to pay.

## Recommended Next Build Order

1. Add `docs/demo-script.md` and a clean judging fallback plan.
2. Add real or anonymized PDF/text fixtures with expected extraction snapshots.
3. Add a demo data reset command or UI control.
4. Add GitHub Actions for tests and smoke checks.
5. Draft privacy/terms documents before any public deployment.
6. Choose the public beta architecture: FastAPI + PostgreSQL + hosted static frontend, or a simpler single-server deployment.
7. Add an LLM provider adapter only after fixtures make it possible to measure whether the provider improves accuracy.

## Release Gate

DocMate should not be treated as production-ready until all of the following are true:

- Public users can sign in and only access their own history.
- Uploaded data handling is documented and implemented consistently.
- Real-document fixture results are measured and reviewed.
- Unsupported or risky files fail clearly.
- The service is deployed with HTTPS, monitoring, backups, and rollback steps.
- Eligibility output continues to show source evidence and conservative uncertainty handling.

