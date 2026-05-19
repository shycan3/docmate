# Frontend Refresh Change Log

**Purpose:** record the UI/UX improvements made after MVP completion so Codex can read the delta without diffing the full workspace.

## Summary

The frontend was updated to feel more polished and more useful on first use.

Main outcome:

- The landing area now explains the product value more clearly.
- Users can try a built-in sample without selecting a file first.
- Profile fields are preserved locally between visits.
- The upload area exposes a clearer action set: analyze, load sample, reset.
- The visual system is more modern, with softer cards, stronger spacing, and improved hierarchy.

## Files Changed

- [frontend/index.html](../../../frontend/index.html)
- [frontend/src/app.js](../../../frontend/src/app.js)
- [frontend/src/styles.css](../../../frontend/src/styles.css)

## What Changed

### 1. Hero and value proposition

The top of the page was changed from a short title into a fuller hero section.

Behavioral effect:

- The user sees what DocMate does before interacting with the form.
- The page now communicates the main value in one sentence plus supporting copy.
- Feature chips make the key affordances visible immediately.

Implementation detail:

- Added a `hero-copy` wrapper.
- Added `lede` text for a short descriptive paragraph.
- Added `hero-chips` to summarize the main product behaviors.

### 2. File upload and action row

The upload card now provides three explicit actions instead of only a single submit button.

New actions:

- Analyze the selected file.
- Load the built-in sample flow.
- Reset the form and hide prior results.

Why this matters:

- New users can test the product immediately without preparing a document.
- Reset gives a safe recovery path when the form is partially filled or the wrong file was selected.
- The upload card now reads like a guided workflow instead of a single input.

Implementation detail:

- Added `sampleButton` and `resetButton` in the HTML.
- Added a short `upload-note` instruction under the upload area.
- Added a `button-row` layout so secondary actions are visible but not dominant.

### 3. Sample flow integration

The frontend now consumes the backend sample path through the existing analysis endpoint.

Behavior:

- Clicking sample does not require a file input.
- The frontend submits `use_sample=true` with the current profile payload.
- The response renders through the same result pipeline as normal uploads.

Why this is important:

- It makes the app demoable in one click.
- It keeps sample behavior aligned with the backend instead of duplicating sample logic in the browser.

Implementation detail:

- `analyze()` now accepts an options object.
- When `useSample` is true, the request posts only `profile` plus `use_sample`.

### 4. Draft persistence for profile fields

Profile inputs are now saved locally and restored on reload.

Behavior:

- Age, grade, region, occupation, income decile, and enrolled status are persisted in `localStorage`.
- The draft is restored automatically on page load.
- Reset clears the visible form state and rewrites the stored draft state to the current empty values.

Why this is important:

- Repeated form entry was the biggest friction point.
- Keeping the draft reduces repetitive input for users comparing multiple notices.

Implementation detail:

- Added `DRAFT_STORAGE_KEY`.
- Added `saveDraft()` and `restoreDraft()` helpers.
- Bound input and change events on the profile fields to persist each update.

### 5. Busy-state handling

The UI now reflects when an analysis or sample load is in progress.

Behavior:

- Buttons become disabled during active requests.
- Button labels change so the user sees what is happening.

This reduces double-submits and makes the interface feel more responsive.

### 6. Visual redesign

The styling was adjusted to create a more modern and calmer product feel.

Changes include:

- Softer background gradients and subtle overlay texture.
- Larger hero typography and a clearer content hierarchy.
- More rounded cards and inputs.
- Stronger contrast for primary actions and softer secondary actions.
- Better focus states for keyboard use.
- Improved mobile layout for action buttons and stacked content.

## Resulting UX Flow

The current browser flow is now:

1. User lands on a page that explains the tool and its key features.
2. User can either fill in a profile or load the sample immediately.
3. User uploads a document or uses the sample path.
4. User receives structured eligibility, extracted fields, warnings, checklist items, and action links.
5. User can reset the form and continue testing without re-entering all fields.

## Validation

Validated after the change:

- `node --check frontend/src/app.js`
- `python -m unittest discover -s tests -p "test_*.py"`

Both checks passed.

## Notes for Future Codex Work

- The frontend is still dependency-light and no-build by design.
- If a larger redesign is needed later, this refresh should be treated as the baseline instead of being rewritten.
- A future React migration should preserve the same sample flow, draft persistence behavior, and result sections.
- The backend already exposes `/api/sample`, so future UI work can keep reusing that contract.