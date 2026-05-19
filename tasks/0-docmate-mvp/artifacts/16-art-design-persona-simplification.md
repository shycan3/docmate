# Art Design Persona Simplification

**Updated:** 2026-05-19  
**Status:** Ten art/design persona reviews completed and reflected in the UI

## Goal

Reduce visual clutter and make DocMate usable without verbal explanation.

## Review Summary

Ten art/design personas reviewed the running web app:

- Web designer.
- UX designer.
- Information designer.
- Typography designer.
- Brand designer.
- Accessibility designer.
- Interaction designer.
- Mobile UI designer.
- Visual editorial designer.
- Presentation/exhibition designer.

The full review log is in `docs/art-design-feedback.md`.

## Implemented Changes

- Simplified the first screen into a compact header, status strip, tabs, and two-step work area.
- Removed large judge-facing text blocks from the product surface.
- Hid demo progress unless demo mode is active.
- Reduced sample card copy.
- Lowered secondary button and label emphasis.
- Made the brand mark blue instead of black.
- Collapsed evidence and guidance sections.
- Made comparison UI quieter until selections exist.

## Verification Target

Browser verification should confirm:

- The first screen has no large judge/explainer block.
- Demo progress is hidden before demo mode.
- The primary action remains `분석하기`.
- Sample analysis is visually secondary.
- Result sections render without horizontal overflow.

Screenshot: `tasks/0-docmate-mvp/artifacts/docmate-simplified-design.png`
