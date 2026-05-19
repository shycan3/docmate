# DocMate Persona Feedback Review

**Updated:** 2026-05-19  
**Review type:** Persona-based hands-on browser review of the local demo at `http://127.0.0.1:8000/`

## Method

Codex drove the running local web app as 10 distinct personas. Each persona had a concrete task and interacted with the product surface instead of only reading the code or static screenshots.

The review focused on presentation readiness:

- Can a first-time visitor understand the service quickly?
- Can a presenter run the demo repeatedly without cleanup friction?
- Does the product preserve user-entered profile data?
- Does the result feel trustworthy enough for a competition demo?
- Are saved analyses and comparison usable during a live pitch?

This was not a statistically valid user study. It was a structured product rehearsal using realistic persona goals.

## Persona Runs

| Persona | Task Performed In The App | Browser Observation | Feedback |
| --- | --- | --- | --- |
| P1 Seoul first-year student | Ran the Seoul scholarship sample. | Result showed `신청 가능`, 10 evidence items, 6 warnings, and export enabled. | The first run is clear and confidence-building. A presenter still needs a visible flow cue for what to show next. |
| P2 Student worried about income decile | Entered a custom Seoul student profile with income decile 8, then ran the Seoul sample. | The profile was overwritten by the sample default income decile 5. | This is confusing. Sample notices should be analyzable with the user's current profile. |
| P3 Graduate student | Ran the graduate scholarship sample. | Result showed graduate-specific documents, warnings, evidence, and export enabled. | Required documents and warning separation are useful. Evidence reduces anxiety about automated analysis. |
| P4 Busan job-seeking youth | Ran the Busan youth-policy sample. | Result showed policy-specific checklist and evidence. | The checklist is useful. Sample cards should show which profile assumptions will be used. |
| P5 Parent/guardian | Ran the Seoul sample and inspected evidence. | Evidence cards and warning counts were visible. | Source snippets make the result more believable for a non-expert reviewer. |
| P6 University support staff | Ran demo mode and inspected history comparison. | Demo mode created sample analyses and opened a two-card comparison panel. | Comparison is strong for counseling. Rehearsal cleanup is cumbersome without a clear-all/reset path. |
| P7 Competition judge | Ran demo mode as a short evaluation flow. | The app jumped to comparison after analysis, but no on-screen presentation queue existed. | Demo mode is strong, but the service needs a visible 3-minute pitch cue. |
| P8 Keyboard-focused user | Opened history and pressed Enter on a focused history item. | The item had focus behavior but did not open from Enter. | History items should open with keyboard activation, not only mouse clicks. |
| P9 Privacy-sensitive user | Opened history and looked for cleanup controls. | Individual delete buttons existed, but no whole-history reset existed. | A local demo handling profile data should offer a full history reset. |
| P10 Presenter | Checked demo mode, export, sample cards, and presentation cues. | Demo and export existed; presentation guide and reset did not. | The demo needs a visible run order, reset button, and sample profile hints for smoother rehearsal. |

## Decision Matrix

| Feedback | Decision | Reason |
| --- | --- | --- |
| Preserve user profile when analyzing a selected sample. | Implemented now. | This directly fixes a real task failure from P2 and makes sample analysis usable for custom scenarios. |
| Add visible presentation queue. | Implemented now. | Helps the presenter and judge follow the intended 3-minute demo without extra explanation. |
| Add full demo/history reset. | Implemented now. | Important for repeated rehearsals and privacy-sensitive local use. |
| Show sample profile hints on sample cards. | Implemented now. | Makes sample assumptions visible before running a demo. |
| Enable keyboard activation for history items. | Implemented now. | Small change with clear accessibility value. |
| Add real OCR, cloud accounts, and OAuth reminders. | Deferred. | These are beta/production items, not needed to harden the local presentation demo. |
| Add more real-world fixtures. | Deferred to next build. | Still important, but larger than the immediate UI/demo hardening pass. |

## Implemented Changes

- `선택 샘플 분석` now analyzes the selected sample with the profile currently in the form.
- Blank-profile sample runs still fall back to the sample's default profile through the backend.
- Added a top-level `발표 큐` panel with the 3-minute demo sequence.
- Added `데모 기록 초기화` in the main control area.
- Added `DELETE /api/analyses` for clearing local saved analysis history.
- Added sample-profile tags to sample cards.
- Added Enter/Space keyboard activation for history items.
- Added a visible focus state for history items.
- Added test coverage for clearing the full analysis history.

## Follow-Up Items

- Add 5 or more real or anonymized notice fixtures.
- Add a short video or GIF of the final demo flow.
- Add a lightweight privacy/retention note before public beta.
- Add GitHub Actions so every push runs backend and frontend checks.

