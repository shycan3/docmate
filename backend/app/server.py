from __future__ import annotations

import cgi
import io
import json
import mimetypes
import posixpath
import sys
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .analyzer import analyze_document
from .models import Profile
from .parser import extract_text_from_upload
from .sample_data import (
    get_sample,
    get_sample_profile,
    list_samples,
)
from .storage import get_storage

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FRONTEND_DIR = ROOT / "frontend"
PROFILE_FIELDS = ("age", "grade", "region", "occupation", "income_decile", "enrolled")


def create_server(
    host: str = "127.0.0.1", port: int = 8000, frontend_dir: str | Path | None = None
) -> ThreadingHTTPServer:
    frontend_path = Path(frontend_dir) if frontend_dir else DEFAULT_FRONTEND_DIR
    handler_class = partial(DocMateRequestHandler, frontend_dir=frontend_path)
    return ThreadingHTTPServer((host, port), handler_class)


def run(host: str = "127.0.0.1", port: int = 8000, frontend_dir: str | Path | None = None) -> None:
    server = create_server(host=host, port=port, frontend_dir=frontend_dir)
    try:
        print(f"DocMate server listening on http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


class DocMateRequestHandler(BaseHTTPRequestHandler):
    server_version = "DocMateHTTP/0.1"

    def __init__(self, *args, frontend_dir: Path, **kwargs) -> None:
        self.frontend_dir = Path(frontend_dir)
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        if path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return
        if path == "/api/samples":
            self._send_json(HTTPStatus.OK, {"samples": list_samples()})
            return
        if path == "/api/sample":
            sample_id = _query_value(parsed_url.query, "sample_id")
            try:
                self._send_json(HTTPStatus.OK, _build_sample_payload(sample_id))
            except KeyError:
                self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Sample not found"})
            return
        if path == "/api/analyses":
            storage = get_storage()
            analyses = storage.list_all()
            self._send_json(HTTPStatus.OK, {"analyses": analyses})
            return
        if path.startswith("/api/analyses/"):
            analysis_id = path.split("/")[-1]
            storage = get_storage()
            analysis = storage.get(analysis_id)
            if analysis:
                self._send_json(HTTPStatus.OK, analysis)
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Analysis not found"})
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/analyze":
            self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Not found"})
            return

        try:
            filename, text, profile = self._parse_analysis_request()
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"detail": str(exc)})
            return

        if not text:
            self._send_json(HTTPStatus.BAD_REQUEST, {"detail": "No analyzable text provided."})
            return

        result = analyze_document(text, profile)
        payload = result.to_dict()
        payload["source"] = {"filename": filename, "text": text}
        payload["profile"] = profile.to_dict()
        
        # Auto-save to storage
        try:
            storage = get_storage()
            analysis_id = storage.save(
                filename=filename,
                document_text=text,
                profile=profile.to_dict(),
                extraction=result.extraction.to_dict(),
                eligibility=result.eligibility.to_dict(),
                warnings=[w.to_dict() for w in result.warnings],
                checklist=[c.to_dict() for c in result.checklist],
                actions=[a.to_dict() for a in result.actions],
                evidence=[item.to_dict() for item in result.evidence],
            )
            payload["id"] = analysis_id  # Include ID in response
        except Exception as e:
            # Silently fail on save (don't break the analysis flow)
            print(f"Warning: Failed to save analysis: {e}")
        
        self._send_json(HTTPStatus.OK, payload)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        
        if path.startswith("/api/analyses/"):
            analysis_id = path.split("/")[-1]
            storage = get_storage()
            if storage.delete(analysis_id):
                self._send_json(HTTPStatus.NO_CONTENT, {})
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Analysis not found"})
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Not found"})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _parse_analysis_request(self) -> tuple[str, str, Profile]:
        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length else b""

        if content_type.startswith("application/json"):
            return _parse_json_payload(body)
        if content_type.startswith("multipart/form-data"):
            return _parse_multipart_payload(content_type, body, self.headers)
        if content_type.startswith("application/x-www-form-urlencoded"):
            return _parse_urlencoded_payload(body)
        raise ValueError("Unsupported Content-Type. Use JSON or multipart form data.")

    def _serve_static(self, raw_path: str) -> None:
        relative_path = posixpath.normpath(raw_path.lstrip("/")) if raw_path else ""
        if relative_path in {"", "."}:
            relative_path = "index.html"

        file_path = (self.frontend_dir / relative_path).resolve()
        try:
            file_path.relative_to(self.frontend_dir.resolve())
        except ValueError:
            self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Not found"})
            return

        if file_path.exists() and file_path.is_file():
            self._send_file(file_path)
            return

        if relative_path == "index.html":
            self._send_placeholder_frontend()
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Not found"})

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path) -> None:
        content = file_path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(file_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_placeholder_frontend(self) -> None:
        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>DocMate</title></head><body>"
            "<main><h1>DocMate backend is running</h1>"
            "<p>The frontend workspace will be served from /frontend when phase 2 is complete.</p>"
            "</main></body></html>"
        ).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


def _parse_json_payload(body: bytes) -> tuple[str, str, Profile]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON body.") from exc

    use_sample = bool(payload.get("use_sample"))
    profile = Profile.from_dict(payload.get("profile"))

    if use_sample and not payload.get("text") and not payload.get("content"):
        sample = _get_requested_sample(payload.get("sample_id"))
        return (
            sample.filename,
            sample.text,
            _profile_or_sample_profile(profile, sample.id),
        )

    filename = str(payload.get("filename") or "upload.txt")
    text = payload.get("text")
    if text is None and payload.get("content") is not None:
        content_value = payload["content"]
        if isinstance(content_value, str):
            text = content_value
        else:
            raise ValueError("JSON content must be a string.")
    if text is None:
        raise ValueError("JSON body must include text or use_sample.")

    return filename, str(text), profile


def _parse_multipart_payload(
    content_type: str, body: bytes, headers
) -> tuple[str, str, Profile]:
    environ = {
        "REQUEST_METHOD": "POST",
        "CONTENT_TYPE": content_type,
        "CONTENT_LENGTH": str(len(body)),
    }
    form = cgi.FieldStorage(
        fp=io.BytesIO(body),
        headers=headers,
        environ=environ,
        keep_blank_values=True,
    )

    profile_payload = {}
    profile_json = _get_form_value(form, "profile")
    if profile_json:
        try:
            profile_payload.update(json.loads(profile_json))
        except json.JSONDecodeError as exc:
            raise ValueError("profile field must be valid JSON.") from exc

    for field in PROFILE_FIELDS:
        value = _get_form_value(form, field)
        if value not in (None, ""):
            profile_payload[field] = value
    profile = Profile.from_dict(profile_payload)

    use_sample = _get_form_value(form, "use_sample")
    if _is_truthy(use_sample) and not _has_file(form, "file") and not _get_form_value(form, "text"):
        sample = _get_requested_sample(_get_form_value(form, "sample_id"))
        return sample.filename, sample.text, _profile_or_sample_profile(profile, sample.id)

    text = _get_form_value(form, "text")
    if text:
        filename = str(_get_form_value(form, "filename") or "upload.txt")
        return filename, text, profile

    if _has_file(form, "file"):
        item = form["file"]
        filename = item.filename or "upload.bin"
        file_bytes = item.file.read()
        return filename, extract_text_from_upload(filename, file_bytes), profile

    raise ValueError("Multipart form must include text, file, or use_sample.")


def _parse_urlencoded_payload(body: bytes) -> tuple[str, str, Profile]:
    try:
        raw = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Invalid form body.") from exc

    values = {}
    for part in raw.split("&"):
        if not part:
            continue
        name, _, value = part.partition("=")
        values[name] = value.replace("+", " ")
    profile = Profile.from_dict({field: values.get(field) for field in PROFILE_FIELDS})
    text = values.get("text", "")
    if not text:
        raise ValueError("Form body must include text.")
    return values.get("filename", "upload.txt"), text, profile


def _get_form_value(form: cgi.FieldStorage, name: str) -> str | None:
    if name not in form:
        return None
    item = form[name]
    if isinstance(item, list):
        item = item[0]
    if getattr(item, "filename", None):
        return None
    return item.value


def _has_file(form: cgi.FieldStorage, name: str) -> bool:
    if name not in form:
        return False
    item = form[name]
    if isinstance(item, list):
        item = item[0]
    return bool(getattr(item, "filename", None) and getattr(item, "file", None))


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _query_value(query: str, key: str) -> str | None:
    values = parse_qs(query).get(key)
    if not values:
        return None
    return values[0]


def _get_requested_sample(sample_id: object | None):
    try:
        return get_sample(str(sample_id).strip() if sample_id else None)
    except KeyError as exc:
        raise ValueError("Unknown sample_id.") from exc


def _profile_or_sample_profile(profile: Profile, sample_id: str) -> Profile:
    if any(value is not None for value in profile.to_dict().values()):
        return profile
    return get_sample_profile(sample_id)


def _build_sample_payload(sample_id: str | None = None) -> dict:
    sample = get_sample(sample_id)
    profile = sample.profile()
    analysis = analyze_document(sample.text, profile)
    return {
        "sample": sample.to_metadata(),
        "document": {"filename": sample.filename, "text": sample.text},
        "profile": profile.to_dict(),
        "analysis": analysis.to_dict(),
    }
