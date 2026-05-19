# DocMate Judge Persona Review

**Updated:** 2026-05-19  
**Review type:** Critic-style judge persona review using the running local web app at `http://127.0.0.1:8000/`

## Method

Five judge personas visited and exercised the local demo. Unlike the earlier user-persona review, these personas evaluated DocMate as a competition submission.

Each judge performed at least one real product action:

- Inspect the first screen and presentation queue.
- Run `데모 모드 실행`.
- Open history comparison.
- Open a saved result.
- Run an ineligible edge case with a custom income profile.
- Inspect trust and local data-handling surfaces.

## Judge Runs

| Judge Persona | Evaluation Criteria | Product Action | Observation | Critique |
| --- | --- | --- | --- | --- |
| J1 Product/problem judge | Is the problem and value clear before the presenter explains it? | Inspected the first screen and presentation queue. | The console and demo queue were clear, but no judge-facing summary block existed. | The app needed a compact problem/value/proof brief on the screen. |
| J2 Presentation/demo judge | Can the value be understood in 3 minutes? | Ran demo mode and inspected the comparison panel. | Demo mode completed and showed two comparison cards. | The comparison was useful but too numeric; it needed a quick judgment memo. |
| J3 Technical/trust judge | Can the result be verified from inputs and source evidence? | Opened a saved result and checked status, evidence, and summary stats. | Evidence existed, but there was no dedicated profile snapshot or decision summary. | The result needed a visible "used profile" and decision rationale block. |
| J4 Edge-case/quality judge | Does an ineligible case explain itself? | Ran the Seoul sample with income decile 8. | The result became `신청 불가` and preserved income decile 8. | The reason was correct, but it should be faster to scan in the result structure. |
| J5 Privacy/business judge | Does the local demo reduce data-handling concerns? | Inspected reset, trust note, and history state. | Full reset existed, but no data-handling note was visible in the result. | The UI should state that original files are not stored and records can be cleared. |

## Decisions

| Feedback | Decision | Reason |
| --- | --- | --- |
| Add judge-facing problem/value/proof summary. | Implemented. | It helps a judge understand the service before the spoken pitch catches up. |
| Add comparison judgment memo. | Implemented. | It turns comparison cards from raw metrics into an immediate decision aid. |
| Add decision summary to result. | Implemented. | It makes eligibility rationale scannable, especially for ineligible cases. |
| Add profile snapshot to result. | Implemented. | It makes the analysis auditable: judges can see which inputs drove the result. |
| Add visible data-handling note. | Implemented. | It reduces privacy concerns during a local demo and supports the full-reset workflow. |
| Add OCR, accounts, billing, or cloud deployment now. | Deferred. | These remain public-beta or production roadmap items, not presentation-demo blockers. |

## Implemented Changes

- Added `심사 포인트` cards to the top of the console.
- Added `판정 요약` to the result screen.
- Added `사용 프로필` to the result screen.
- Added `판단 메모` to comparison cards.
- Added `데이터 처리` note to the result screen.

## Remaining Judge Risks

- The demo still relies on curated built-in samples, so real-world fixture breadth should be the next proof point.
- OCR and cloud account support remain outside the local MVP.
- A short demo video would reduce live-presentation risk.

