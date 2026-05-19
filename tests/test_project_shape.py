from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectShapeTests(unittest.TestCase):
    def test_required_runtime_files_exist(self) -> None:
        required = [
            "backend/run.py",
            "backend/app/server.py",
            "backend/app/analyzer.py",
            "frontend/index.html",
            "frontend/src/app.js",
            "frontend/src/styles.css",
            "scripts/check_smoke.py",
            "docs/spec.md",
            "docs/architecture.md",
            "docs/business-model.md",
        ]
        missing = [path for path in required if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_frontend_references_local_assets(self) -> None:
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        self.assertIn('/src/styles.css', html)
        self.assertIn('/src/app.js', html)
        self.assertNotIn('https://', html)


if __name__ == "__main__":
    unittest.main()
