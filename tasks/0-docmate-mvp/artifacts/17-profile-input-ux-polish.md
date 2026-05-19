# Profile Input UX Polish

**Updated:** 2026-05-19  
**Status:** Implemented

## Goal

Remove small but noticeable form frictions from the profile step.

## Findings

- `거주지` was a free-text input even though eligibility rules compare it against known regions such as `서울` and `부산`.
- `직업` was a free-text input even though the analyzer looks for known status keywords such as `대학생`, `구직자`, and `미취업`.
- `학년` was too narrow as a label because the app also supports `졸업`, `석사과정`, and `박사과정`.
- `소득구간` was a number input even though users think of it as a bounded 1-10 choice.

## Changes

- Changed `학년` to `학적` and made it a select input.
- Changed `거주지` to a region select input.
- Changed `직업` to `현재 상태` and made it a select input.
- Changed `소득구간` to a 1-10 select input.
- Updated result profile labels to match the new form language.

## Expected Impact

Users can now complete the profile without guessing exact wording, and the selected values better match the rule-based eligibility checks.

Screenshot: `tasks/0-docmate-mvp/artifacts/docmate-profile-selects.png`
