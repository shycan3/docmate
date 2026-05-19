from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib import request

from backend.app.analyzer import analyze_document
from backend.app.sample_data import SAMPLE_DOCUMENT_TEXT, get_sample_profile
from backend.app.server import create_server


class BackendPipelineTests(unittest.TestCase):
    def test_sample_analysis_contains_core_outputs(self) -> None:
        result = analyze_document(SAMPLE_DOCUMENT_TEXT, get_sample_profile()).to_dict()

        self.assertEqual(result["eligibility"]["status"], "eligible")
        self.assertTrue(result["warnings"])
        self.assertTrue(result["checklist"])
        self.assertTrue(result["actions"])

    def test_server_serves_api_and_frontend(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            frontend_dir = Path(temp_dir)
            (frontend_dir / "index.html").write_text("<!doctype html><h1>DocMate</h1>", encoding="utf-8")
            server = create_server(port=0, frontend_dir=frontend_dir)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                with request.urlopen(f"{base_url}/health") as response:
                    self.assertEqual(json.loads(response.read().decode("utf-8")), {"status": "ok"})
                with request.urlopen(f"{base_url}/") as response:
                    self.assertIn("DocMate", response.read().decode("utf-8"))
            finally:
                server.shutdown()
                thread.join(timeout=2)
                server.server_close()


if __name__ == "__main__":
    unittest.main()
