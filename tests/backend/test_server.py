from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from urllib import error, request

from backend.app.server import create_server


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = os.environ.get("DOCMATE_DB_PATH")
        os.environ["DOCMATE_DB_PATH"] = str(Path(self.temp_dir.name) / "test-docmate.db")
        frontend_dir = Path(self.temp_dir.name)
        (frontend_dir / "index.html").write_text(
            "<!doctype html><html><body><h1>DocMate UI</h1></body></html>",
            encoding="utf-8",
        )
        self.server = create_server(port=0, frontend_dir=frontend_dir)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()
        if self.previous_db_path is None:
            os.environ.pop("DOCMATE_DB_PATH", None)
        else:
            os.environ["DOCMATE_DB_PATH"] = self.previous_db_path
        self.temp_dir.cleanup()

    def test_health_endpoint(self) -> None:
        with request.urlopen(f"{self.base_url}/health") as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(payload, {"status": "ok"})

    def test_sample_endpoint_returns_analysis(self) -> None:
        with request.urlopen(f"{self.base_url}/api/sample") as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertIn("analysis", payload)
        self.assertEqual(payload["analysis"]["eligibility"]["status"], "eligible")

    def test_samples_endpoint_returns_demo_options(self) -> None:
        with request.urlopen(f"{self.base_url}/api/samples") as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(len(payload["samples"]), 3)
        self.assertIn("profile", payload["samples"][0])

    def test_sample_endpoint_accepts_sample_id(self) -> None:
        with request.urlopen(
            f"{self.base_url}/api/sample?sample_id=busan-youth-living-fund"
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(payload["sample"]["id"], "busan-youth-living-fund")
        self.assertEqual(payload["analysis"]["eligibility"]["status"], "eligible")

    def test_json_analysis_endpoint(self) -> None:
        body = json.dumps(
            {
                "filename": "notice.txt",
                "text": "장학금 공고\n신청 기간: 2026-05-01 ~ 2026-05-31\n지원 대상: 서울 거주, 재학생\n신청 URL: https://example.com/apply",
                "profile": {
                    "age": 22,
                    "grade": "3학년",
                    "region": "서울",
                    "occupation": "대학생",
                    "income_decile": 4,
                    "enrolled": True,
                },
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/analyze",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with request.urlopen(req) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(payload["eligibility"]["status"], "eligible")
        self.assertEqual(payload["source"]["filename"], "notice.txt")
        self.assertIn("id", payload)

    def test_multipart_analysis_endpoint(self) -> None:
        boundary = "----DocMateBoundary"
        profile_json = json.dumps(
            {
                "age": 22,
                "grade": "3학년",
                "region": "서울",
                "occupation": "대학생",
                "income_decile": 4,
                "enrolled": True,
            },
            ensure_ascii=False,
        )
        text = (
            "2026 장학금 공고\n"
            "신청 기간: 2026-05-01 ~ 2026-05-31\n"
            "지원 대상: 서울 거주, 재학생\n"
            "제출 서류: 재학증명서\n"
            "신청 URL: https://example.com/apply\n"
        )
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="profile"\r\n\r\n'
            f"{profile_json}\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="notice.txt"\r\n'
            "Content-Type: text/plain; charset=utf-8\r\n\r\n"
            f"{text}\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        req = request.Request(
            f"{self.base_url}/api/analyze",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )

        with request.urlopen(req) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(payload["source"]["filename"], "notice.txt")
        self.assertIn("재학증명서", payload["extraction"]["required_documents"])

    def test_analysis_history_endpoints(self) -> None:
        body = json.dumps(
            {
                "use_sample": True,
                "sample_id": "seoul-hope-scholarship",
                "profile": {},
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/analyze",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with request.urlopen(req) as response:
            created = json.loads(response.read().decode("utf-8"))

        analysis_id = created["id"]

        with request.urlopen(f"{self.base_url}/api/analyses") as response:
            history = json.loads(response.read().decode("utf-8"))
        self.assertTrue(any(item["id"] == analysis_id for item in history["analyses"]))

        with request.urlopen(f"{self.base_url}/api/analyses/{analysis_id}") as response:
            loaded = json.loads(response.read().decode("utf-8"))
        self.assertEqual(loaded["filename"], "sample-1-seoul-hope-scholarship.txt")

        delete_req = request.Request(
            f"{self.base_url}/api/analyses/{analysis_id}",
            method="DELETE",
        )
        with request.urlopen(delete_req) as response:
            self.assertEqual(response.status, 204)

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(f"{self.base_url}/api/analyses/{analysis_id}")
        self.assertEqual(context.exception.code, 404)

    def test_static_frontend_serving(self) -> None:
        with request.urlopen(f"{self.base_url}/") as response:
            body = response.read().decode("utf-8")

        self.assertIn("DocMate UI", body)


if __name__ == "__main__":
    unittest.main()
