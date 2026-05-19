# DocMate Art And Design Persona Review

**Updated:** 2026-05-19  
**Review type:** Visual/design critique using the running local web app at `http://127.0.0.1:8000/`

## Method

Ten art and design personas reviewed the simplified DocMate interface in the browser. The review focused on visual hierarchy, ease of first use, typography, brand tone, interaction clarity, responsive layout, and presentation readability.

The personas did not only inspect static files. They opened the website, reviewed the first screen, ran a sample analysis, opened the result view, and inspected history/comparison behavior where relevant.

## Persona Runs

| Persona | Lens | Product Action | Critique |
| --- | --- | --- | --- |
| A1 Web designer | First-screen hierarchy | Opened the first screen and scanned header, status, form, and sample cards. | The page is quieter, but the demo progress strip still feels presentation-specific before any action. |
| A2 UX designer | Next-action clarity | Compared `분석하기`, sample analysis, and reset buttons. | Primary analysis is visible, but sample analysis should feel less important than the main action. |
| A3 Information designer | Result scanning | Ran the Seoul sample and read the result view. | Status and metrics scan well; `판정 요약` should be visually stronger than `사용 프로필`. |
| A4 Typography designer | Type rhythm | Checked headings, field labels, and result text density. | Type hierarchy is stable, but too many labels are heavy. Secondary labels should be lighter. |
| A5 Brand designer | Tone and color | Reviewed the mark, status colors, and button color. | The black mark feels too heavy for a youth-policy service; a softer blue mark fits better. |
| A6 Accessibility designer | Focus and disclosure | Checked buttons, details elements, and history focus behavior. | Disclosure sections are useful; summaries should keep counts or clear labels. |
| A7 Interaction designer | History/comparison behavior | Opened the history tab and inspected comparison flow. | History is stable, but comparison should stay quiet until selections exist. |
| A8 Mobile UI designer | Touch and top actions | Checked action density and overflow behavior. | Touch targets are sufficient; demo/reset controls should not dominate the top on small screens. |
| A9 Visual editorial designer | Card and border density | Compared repeated cards across analysis and history screens. | Borders are cleaner, but repeated cards can still become busy; reduce competing panels. |
| A10 Presentation/exhibition designer | Distance readability | Reviewed status badges and comparison titles as if projected. | Status badges read well; demo progress should be visible mainly during demo execution. |

## Decisions

| Feedback | Decision | Reason |
| --- | --- | --- |
| Hide demo progress until demo mode is running or complete. | Implemented. | Keeps the everyday workflow clean while preserving presentation support. |
| Lower sample-analysis visual weight. | Implemented. | Makes `분석하기` the obvious primary action. |
| Make `판정 요약` stronger than profile details. | Implemented. | Helps users read the result in the right order. |
| Reduce secondary label weight. | Implemented. | Softens the dense operational interface. |
| Change the brand mark from black to blue. | Implemented. | Keeps trust while feeling less severe. |
| Make comparison panel quiet when empty. | Implemented. | Prevents unused comparison UI from competing with history items. |

## Implemented UI Changes

- Removed large judge-facing and explanatory blocks from the first screen.
- Replaced the prior overview cards with a compact status strip.
- Moved demo controls into a smaller header action area.
- Hid the demo progress strip until demo mode is active.
- Reduced sample-card text and lowered secondary button emphasis.
- Collapsed source evidence and data guidance into disclosure sections.
- Tuned typography weight, card shadows, border radius, and spacing.
- Made the comparison panel visually stronger only after selections exist.

## Remaining Design Notes

- The history list can still become visually dense with many saved records.
- A future filter/search affordance would help once history is used heavily.
- A dedicated presentation mode could keep demo-specific controls away from the normal user path.

