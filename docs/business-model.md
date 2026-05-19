# DocMate Business Model

## Problem

Scholarship and youth-policy notices are abundant, but the application path is still manual. Users must read long PDF notices, translate eligibility conditions into their own situation, list required documents, and remember deadlines.

Common pain points:

- Users spend too much time checking notices they cannot apply for.
- Eligibility conditions are easy to misread, especially around income, region, enrollment, and duplicate-support rules.
- Missing-document and no-edit policies often cause avoidable failures.
- Users comparing several notices have no lightweight way to save and revisit analysis results.

## Solution

DocMate converts a notice into an action screen:

- Structured extraction of period, eligibility, benefits, documents, method, and URL.
- Rule-based profile comparison with `eligible`, `needs_review`, or `ineligible`.
- Risk warnings for duplicate support, no-edit, automatic rejection, missing documents, and nationality limits.
- Checklist generation with document/action links.
- Local history so users can revisit prior analyses without creating an account.

## Target Users

Primary users:

- University students looking for scholarships.
- Young adults applying for local youth-policy benefits.
- Career centers, student councils, and local support desks that help applicants interpret notices.

Early wedge:

- Korean university students and job-seeking youth who already search scholarship and policy notices online.

## Market

Working assumptions for early validation:

- Target population: Korean youth and students who regularly review scholarship or policy notices.
- Frequency: several notices per month during application seasons.
- Willingness to pay: low for one-off use, higher for saved history, comparison, reminders, and institution-backed workflows.

TAM/SAM/SOM should be validated with interviews and usage data rather than treated as fixed truth. A practical first target is not the whole youth market, but users who already apply to several notices per semester.

## Revenue Model

B2C:

- Free: limited monthly analyses, checklist, warnings, and action links.
- Premium: unlimited analyses, saved comparisons, reminders, export, and richer profile matching.

B2B:

- Universities and local governments can offer DocMate as a notice interpretation layer for students or citizens.
- Institution plans can include custom notice templates, dashboards, and admin review workflows.

Partnerships:

- Scholarship platforms, student portals, and youth-policy newsletters can embed or link to DocMate-style analysis.

## Competitive Advantage

- Domain-specific output: DocMate is optimized for scholarship and youth-policy action, not generic PDF summarization.
- Conservative eligibility: the product avoids overclaiming and marks ambiguous cases as `needs_review`.
- Action orientation: warnings, checklist, and calendar/application links are surfaced together.
- Low-friction deployment: the local MVP runs with Python, static frontend files, PyMuPDF, and SQLite.

## Go-To-Market

1. Pilot with a small group of students applying to scholarships in one semester.
2. Collect failure cases and expand fixtures with real notices.
3. Add comparison/reminder features that justify premium usage.
4. Approach university support teams with pilot metrics.
5. Expand from scholarship notices to local youth-policy notices.

## Key Metrics

- Analysis completion rate.
- Percentage of users who open application or document links.
- Number of notices analyzed per user.
- Saved-history reuse rate.
- User-reported time saved per notice.
- False positive and false negative eligibility feedback.

## Risks

- Eligibility errors can harm trust, so uncertain cases must stay conservative.
- Real-world notices vary widely in formatting, so parser fixtures need to grow.
- Users may not pay for occasional analysis, making B2B and seasonal premium features important.
- Calendar, portal, and document issuance integrations add setup complexity and should wait until usage proves demand.

## Next Validation Step

Run a small study with 20 to 50 target users. Ask each user to analyze at least three real notices, then measure whether DocMate reduced reading time, improved confidence, and helped them avoid missing documents or risky conditions.
