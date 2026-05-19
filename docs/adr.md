# DocMate MVP ADR

## ADR-001: Ship A Dependency-Light MVP First

### Decision

Use the Python standard library and a no-build frontend as the baseline implementation path.

### Why

- The execution environment may block package installation.
- The project still needs a full demo and test flow without external setup.
- Local reliability matters more than framework fidelity in the first milestone.

### Consequences

- The current MVP uses `http.server` instead of FastAPI.
- The frontend uses plain JavaScript instead of React.
- The architecture must preserve upgrade seams for the originally planned stack.

## ADR-002: Keep A Deterministic Sample Provider

### Decision

Include built-in sample data and deterministic analysis behavior that work without API keys.

### Why

- The product must remain demoable in restricted environments.
- Tests should not depend on network access or model variance.
- Early product validation is about workflow usefulness, not model-provider sophistication.

### Consequences

- Sample outputs must be stable across runs.
- Real LLM integrations remain optional extension points.

## ADR-003: Prefer Conservative Eligibility Outcomes

### Decision

Return `needs_review` whenever conditions are incomplete, ambiguous, or too complex for safe rule evaluation.

### Why

- A false "eligible" result is more harmful than asking the user to verify a condition.
- Scholarship and policy announcements often contain exceptions and edge cases.
- The MVP only guarantees high confidence on simple rule patterns.

### Consequences

- The product will intentionally avoid over-automation for complex documents.
- Missing profile fields are treated as unresolved, not ignored.

## ADR-004: Make The First Screen The Working Tool

### Decision

The initial UI must open directly into the analysis workspace rather than a marketing landing page.

### Why

- The product value is demonstrated through action, not explanation.
- The user flow starts with upload, profile input, and result inspection.
- The MVP should minimize clicks between arrival and analysis.

### Consequences

- The frontend prioritizes form and result density over promotional content.
- Empty, loading, error, and result states are product-critical.

## ADR-005: Exclude Login And OAuth From The MVP

### Decision

Do not implement login or real calendar write access in the first milestone.

### Why

- These features add setup and operational complexity without validating the core insight.
- The immediate product question is whether action-oriented document analysis is useful.

### Consequences

- Calendar support is limited to links or generated artifacts rather than direct account integration.
- User intervention for keys and OAuth remains documented separately.

## ADR-006: Use Local SQLite For Analysis History

### Decision

Persist completed analysis records to a local SQLite database.

### Why

- Saved history makes the product feel stateful without requiring accounts or cloud setup.
- SQLite is included with Python and keeps the local demo simple.
- History is useful for comparing multiple notices during a scholarship search.

### Consequences

- `POST /api/analyze` returns an analysis `id` when the save succeeds.
- The frontend can list, reload, and delete saved analyses.
- This is still local-only storage; multi-user sync remains a future extension.

## ADR-007: Surface Source Evidence Before Adding Full AI Reasoning

### Decision

Add concise source evidence snippets to analysis results before introducing a real LLM provider.

### Why

- Presentation users need to trust that DocMate is grounded in the notice text.
- Evidence snippets make rule-based extraction explainable without adding API keys.
- This creates a compatible UI pattern for future LLM citations and confidence scoring.

### Consequences

- `AnalysisResult` now includes an `evidence` list.
- Saved SQLite history stores evidence with each analysis.
- The frontend shows evidence cards near the result summary and includes evidence in Markdown export.
