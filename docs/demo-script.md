# DocMate Demo Script

**Updated:** 2026-05-19  
**Target:** 3-5 minute competition presentation

## Setup

Run the local server:

```bash
python backend/run.py
```

Open:

```text
http://127.0.0.1:8000
```

For a clean rehearsal, click `데모 기록 초기화` before starting.

## Live Flow

1. Start on the main console.
   - Say: DocMate turns scholarship and youth-policy notices into eligibility guidance, warnings, and an action checklist.
   - Point to `심사 포인트` for problem, solution, and proof.

2. Click `데모 모드 실행`.
   - The app analyzes all three built-in samples and opens the history comparison panel.
   - Say: The demo is deterministic and does not need API keys, OAuth, or cloud setup.

3. Show the comparison panel.
   - Point out status, period, benefit summary, document count, risk count, checklist count, and application-link availability.
   - Say: This helps a student compare several notices before deciding where to spend effort.

4. Open one saved analysis.
   - Show eligibility, warnings, checklist, and source evidence.
   - Show `판정 요약` and `사용 프로필`.
   - Say: DocMate stays conservative and surfaces both the user inputs and source snippets so users can verify the basis of the recommendation.

5. Click `결과 내보내기`.
   - Say: The output can become a personal application checklist or a support-center handoff.

6. Close with the trust note.
   - Show `데이터 처리`.
   - Say: DocMate helps users prepare, but final submission still requires checking the official notice and institution instructions.

## Backup Flow

If the browser has stale history, click `데모 기록 초기화` and run demo mode again.

If the backend is not responding:

1. Open `http://127.0.0.1:8000/health`.
2. Confirm it returns `{ "status": "ok" }`.
3. Restart with `python backend/run.py` if needed.

If file upload fails during a live presentation, use the built-in sample cards. The sample flow covers the core service value without external files.
