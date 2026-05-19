# Persona Feedback Demo Hardening

**Updated:** 2026-05-19  
**Status:** Feedback collected from actual browser interaction and implemented

## Goal

Improve the local presentation demo by making 10 personas actually run the website flow, then convert reasonable feedback into product changes.

## Browser Review Summary

10 persona runs were executed against `http://127.0.0.1:8000/`.

The most important findings were:

- Sample analysis overwrote a user's manually entered profile.
- The demo mode worked, but the screen lacked a clear presentation queue.
- Repeated rehearsals created many saved records without a one-click reset.
- Sample cards did not show the profile assumptions behind each sample.
- History cards were focusable but did not open with Enter.

The full feedback log is in `docs/persona-feedback.md`.

## Implemented Changes

- Changed sample analysis so the current form profile is preserved.
- Added a `발표 큐` panel for the 3-minute demo sequence.
- Added a `데모 기록 초기화` button.
- Added `DELETE /api/analyses` to clear local history.
- Added sample-profile tags to sample cards.
- Added keyboard activation and focus styling for history items.
- Added server test coverage for full history clearing.
- Added `docs/demo-script.md`.

Screenshot: `tasks/0-docmate-mvp/artifacts/docmate-demo-hardening.png`

## Deferred

- OCR.
- Real LLM provider adapters.
- Cloud accounts and multi-user sync.
- Google Calendar OAuth.
- Real-world fixture suite.

These remain important, but they are not required for the local presentation demo hardening pass.
