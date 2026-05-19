# DocMate MVP User Intervention

## Current MVP Requirement

No user-managed API key, OAuth configuration, or external service account is required for the local MVP demo and test flow.

The intended baseline experience is:

1. Start the local server.
2. Open the app.
3. Upload a supported file or use the sample announcement.
4. Review the generated analysis.
5. Reopen prior results from the local history tab when needed.

## Manual Actions The User May Still Perform

- Choose a sample announcement instead of uploading a document when testing fallback behavior.
- Verify final application details against the original announcement before submitting to the real institution.
- Open external application or document-issuance links provided by the result screen.
- Delete local history records that are no longer useful.
- Clear all local demo/history records before a presentation rehearsal.
- If a browser tab shows a load failure on `http://127.0.0.1:8000/api/analyses`, start the local server first and confirm `http://127.0.0.1:8000/health` returns `{ "status": "ok" }`.
- Treat `GET /api/analyses` as a JSON history API. It is not the main UI entry point.

## Not Required In This Phase

The following are intentionally not required for MVP completion:

- Claude or OpenAI API key setup
- Google Calendar OAuth
- Database provisioning
- Cloud deployment credentials

## Future Optional Setup

These setup steps may be introduced after the dependency-light MVP is validated:

- `DOCMATE_LLM_PROVIDER` and provider-specific API key variables for real document analysis
- Google OAuth client configuration for direct calendar event creation
- Institution-specific link maps for school portals or government issuance sites

If these future integrations are added, their setup instructions should stay in this document rather than being mixed into the core product spec.
