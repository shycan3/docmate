# Remaining Development Roadmap

**Updated:** 2026-05-19  
**Status:** Documented for continued development and GitHub tracking

## Goal

Identify what remains after the current competition-ready local service build, then turn those gaps into a practical development roadmap.

## Reviewed Sources

- `README.md`
- `docs/spec.md`
- `docs/architecture.md`
- `docs/adr.md`
- `docs/business-model.md`
- `docs/user-intervention.md`
- Existing task artifacts under `tasks/0-docmate-mvp/artifacts/`

## Outcome

Added `docs/roadmap.md` as the canonical remaining-development document.

The roadmap separates work into three readiness targets:

- Competition presentation demo: service is currently about 90-95% ready.
- Public beta: service is currently about 55-60% ready.
- Production launch: service is currently about 40-50% ready.

## Main Remaining Areas

- Presentation hardening: demo script, real fixtures, screenshots/GIFs, demo reset, error-state polish.
- Public beta foundation: cloud deployment, accounts, privacy policy, production database, real-document evaluation, CI.
- Production differentiation: OCR, calendar integration, institution workflows, feedback loop, monitoring, rate limits, payment or pilot packaging.
- Data quality: fixture library, snapshot tests, false positive/negative tracking, confidence metadata.
- Security and privacy: account isolation, retention/deletion rules, upload validation, legal disclaimers.
- Business validation: 20-50 user study, usage metrics, university/support-team pilot discovery.

## Recommended Next Build

1. Write `docs/demo-script.md`.
2. Add 5 or more realistic fixture notices and expected extraction snapshots.
3. Add a local demo-data reset path.
4. Add GitHub Actions for tests and smoke checks.
5. Draft privacy and terms documents before public deployment.

This artifact exists to keep the project history clear; `docs/roadmap.md` should be updated as the active roadmap.

