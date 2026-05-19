from __future__ import annotations

import os

try:
    from backend.app.server import run
except ModuleNotFoundError:
    from app.server import run


def main() -> None:
    host = os.environ.get("DOCMATE_HOST", "127.0.0.1")
    port = int(os.environ.get("DOCMATE_PORT", "8000"))
    print(
        f"DocMate entry point ready: open http://{host}:{port}/ and use /api/analyses for JSON history"
    )
    run(host=host, port=port)


if __name__ == "__main__":
    main()
