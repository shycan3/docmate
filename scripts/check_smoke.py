from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.server import create_server
from backend.app.sample_data import SAMPLE_DOCUMENT_TEXT, get_sample_profile


def main() -> None:
    previous_db_path = os.environ.get("DOCMATE_DB_PATH")
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["DOCMATE_DB_PATH"] = str(Path(temp_dir) / "smoke-docmate.db")
        server = create_server(port=0, frontend_dir=ROOT / "frontend")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"

        try:
            assert_json(f"{base_url}/health", {"status": "ok"})
            samples = get_json(f"{base_url}/api/samples")
            assert len(samples["samples"]) == 3

            sample = get_json(f"{base_url}/api/sample?sample_id=seoul-hope-scholarship")
            assert sample["analysis"]["eligibility"]["status"] == "eligible"
            assert sample["analysis"]["checklist"]

            analysis = post_json(
                f"{base_url}/api/analyze",
                {
                    "filename": "sample-announcement.txt",
                    "text": SAMPLE_DOCUMENT_TEXT,
                    "profile": get_sample_profile().to_dict(),
                },
            )
            assert analysis["eligibility"]["status"] == "eligible"
            assert analysis["actions"]
            assert analysis["id"]

            history = get_json(f"{base_url}/api/analyses")
            assert any(item["id"] == analysis["id"] for item in history["analyses"])

            with request.urlopen(f"{base_url}/") as response:
                html = response.read().decode("utf-8")
            assert "DocMate" in html
            assert "/src/app.js" in html
            assert "panelHistory" in html
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()
            if previous_db_path is None:
                os.environ.pop("DOCMATE_DB_PATH", None)
            else:
                os.environ["DOCMATE_DB_PATH"] = previous_db_path

    print("DocMate smoke check passed.")


def get_json(url: str) -> dict:
    with request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def assert_json(url: str, expected: dict) -> None:
    actual = get_json(url)
    assert actual == expected, actual


if __name__ == "__main__":
    main()
