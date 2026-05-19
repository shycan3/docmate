# Day 1 Implementation: Backend Enhancement (PyMuPDF + SQLite)

**Document Version:** 1.0  
**Date:** 2026-05-20  
**Estimated Duration:** 4-5 hours  
**Status:** Ready for Implementation

---

## Part 1: PyMuPDF Integration (1.5 hours)

### 1.1 Installation & Setup

**Command:**
```bash
pip install PyMuPDF
```

**Verification:**
```bash
python -c "import fitz; print(fitz.version)"
```

**Expected Output:**
```
('1.x.x', '...')
```

### 1.2 Modify `backend/app/parser.py`

**Current Implementation:**
```python
def extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    if not filename:
        return "(no filename)"
    
    if filename.endswith(".txt") or filename.endswith(".text"):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return "(text decoding failed)"
    
    return "PDF 또는 텍스트 파일 업로드..."
```

**New Implementation:**
```python
import fitz  # PyMuPDF

def extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    if not filename:
        return "(no filename)"
    
    # Handle text files
    if filename.endswith(".txt") or filename.endswith(".text"):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return "(text decoding failed)"
    
    # Handle PDF files
    if filename.endswith(".pdf"):
        try:
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            pdf_document.close()
            
            full_text = "\n".join(text_parts)
            if full_text.strip():
                return full_text
            else:
                return "(PDF has no extractable text)"
        except Exception as e:
            # Fallback for corrupted or image-based PDFs
            return f"(PDF processing failed: {type(e).__name__})"
    
    # Unsupported format
    return f"(unsupported format: {filename})"
```

**Why This Design:**
1. **Text files**: 기존대로 UTF-8 디코딩
2. **PDF files**: PyMuPDF로 모든 페이지 추출
3. **Fallback**: PDF 처리 실패 시 → 에러 메시지 (명확하게)
4. **Future-proof**: 이미지 기반 PDF는 나중에 OCR 추가 가능

### 1.3 Testing

**Test File:** `tests/backend/test_parser.py` (신규)

```python
import unittest
from backend.app.parser import extract_text_from_upload

class TestPdfExtraction(unittest.TestCase):
    def test_extract_text_file(self):
        text_content = "Sample text content"
        result = extract_text_from_upload("test.txt", text_content.encode("utf-8"))
        self.assertEqual(result, text_content)
    
    def test_extract_pdf_empty(self):
        # Minimal valid PDF with no text
        minimal_pdf = b"%PDF-1.0\n1 0 obj\n<</Type/Catalog>>\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<</Size 1>>\nstartxref\n0\n%%EOF"
        result = extract_text_from_upload("test.pdf", minimal_pdf)
        # Should handle gracefully (either empty or error message)
        self.assertIsInstance(result, str)
    
    def test_unsupported_format(self):
        result = extract_text_from_upload("test.doc", b"some binary")
        self.assertIn("unsupported", result)
```

**Run Test:**
```bash
python -m unittest tests.backend.test_parser
```

---

## Part 2: SQLite Storage Layer (2 hours)

### 2.1 Database Schema & `storage.py` (New File)

**File:** `backend/app/storage.py`

**Design:**
- Single table: `analyses` (stores all analysis data as JSON)
- Primary key: `id` (UUID)
- Timestamps: `created_at` (for sorting)
- Immutable: write-once, read-many (no updates)

**Implementation:**

```python
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import asdict

class AnalysisStorage:
    def __init__(self, db_path: str = "docmate.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    document_text TEXT,
                    profile TEXT,
                    extraction TEXT,
                    eligibility TEXT,
                    warnings TEXT,
                    checklist TEXT,
                    actions TEXT
                )
            """)
            conn.commit()
    
    def save(self, filename: str, document_text: str, profile: dict, 
             extraction: dict, eligibility: dict, warnings: list, 
             checklist: list, actions: list) -> str:
        """
        Save analysis result and return the ID.
        
        Returns:
            str: UUID of the saved analysis
        """
        analysis_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO analyses 
                (id, created_at, filename, document_text, profile, 
                 extraction, eligibility, warnings, checklist, actions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                created_at,
                filename,
                document_text,
                json.dumps(profile, ensure_ascii=False),
                json.dumps(extraction, ensure_ascii=False),
                json.dumps(eligibility, ensure_ascii=False),
                json.dumps(warnings, ensure_ascii=False),
                json.dumps(checklist, ensure_ascii=False),
                json.dumps(actions, ensure_ascii=False)
            ))
            conn.commit()
        
        return analysis_id
    
    def get(self, analysis_id: str) -> Optional[dict]:
        """Retrieve a single analysis by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM analyses WHERE id = ?", 
                (analysis_id,)
            )
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def list_all(self, limit: int = 50) -> List[dict]:
        """Retrieve all analyses, ordered by creation date (newest first)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def delete(self, analysis_id: str) -> bool:
        """Delete an analysis by ID. Returns True if deleted, False if not found."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM analyses WHERE id = ?",
                (analysis_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """Convert SQL row to dictionary with parsed JSON fields."""
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "filename": row["filename"],
            "document_text": row["document_text"],
            "profile": json.loads(row["profile"] or "{}"),
            "extraction": json.loads(row["extraction"] or "{}"),
            "eligibility": json.loads(row["eligibility"] or "{}"),
            "warnings": json.loads(row["warnings"] or "[]"),
            "checklist": json.loads(row["checklist"] or "[]"),
            "actions": json.loads(row["actions"] or "[]")
        }
    
    def clear_all(self):
        """Clear all analyses (for testing only)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM analyses")
            conn.commit()

# Global storage instance
_storage_instance: Optional[AnalysisStorage] = None

def get_storage(db_path: str = "docmate.db") -> AnalysisStorage:
    """Get or create the global storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = AnalysisStorage(db_path)
    return _storage_instance
```

**Key Design Decisions:**
1. **UUID for ID**: No guessable IDs, no collisions
2. **UTC timestamps**: Consistent across timezones
3. **JSON storage**: Flexible, no schema changes needed later
4. **Singleton pattern**: Only one DB connection per process
5. **Simple CRUD**: Exactly what we need, nothing more

### 2.2 Modify `backend/app/server.py`

**Additions to import section:**
```python
from .storage import get_storage
import json
```

**Add new endpoint handlers:**

```python
def do_GET(self):
    # ... existing code ...
    
    elif path == "/api/analyses":
        storage = get_storage()
        analyses = storage.list_all()
        self._send_json(HTTPStatus.OK, {"analyses": analyses})
    
    elif path.startswith("/api/analyses/"):
        analysis_id = path.split("/")[-1]
        storage = get_storage()
        analysis = storage.get(analysis_id)
        if analysis:
            self._send_json(HTTPStatus.OK, analysis)
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Analysis not found"})

def do_DELETE(self):
    path = self.path.split("?")[0]
    
    if path.startswith("/api/analyses/"):
        analysis_id = path.split("/")[-1]
        storage = get_storage()
        if storage.delete(analysis_id):
            self._send_json(HTTPStatus.NO_CONTENT, {})
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Analysis not found"})
    else:
        self._send_json(HTTPStatus.NOT_FOUND, {"detail": "Not found"})
```

**Modify `do_POST` to save results:**

Find this section in `do_POST` after `_handle_analyze`:
```python
def _handle_analyze(self):
    # ... existing code ...
    analysis = analyze_document(document_text, profile)
    
    response = {
        "extraction": extraction.to_dict(),
        "eligibility": eligibility.to_dict(),
        "warnings": [w.to_dict() for w in warnings],
        "checklist": [c.to_dict() for c in checklist],
        "actions": [a.to_dict() for a in actions],
    }
    self._send_json(HTTPStatus.OK, response)
```

**Change to:**
```python
def _handle_analyze(self):
    # ... existing code ...
    analysis = analyze_document(document_text, profile)
    
    response = {
        "extraction": extraction.to_dict(),
        "eligibility": eligibility.to_dict(),
        "warnings": [w.to_dict() for w in warnings],
        "checklist": [c.to_dict() for c in checklist],
        "actions": [a.to_dict() for a in actions],
    }
    
    # Auto-save to storage
    try:
        storage = get_storage()
        analysis_id = storage.save(
            filename=filename,
            document_text=document_text,
            profile=profile.to_dict(),
            extraction=extraction.to_dict(),
            eligibility=eligibility.to_dict(),
            warnings=[w.to_dict() for w in warnings],
            checklist=[c.to_dict() for c in checklist],
            actions=[a.to_dict() for a in actions]
        )
        response["id"] = analysis_id  # Include ID in response
    except Exception as e:
        # Silently fail on save (don't break the analysis flow)
        print(f"Warning: Failed to save analysis: {e}")
    
    self._send_json(HTTPStatus.OK, response)
```

### 2.3 Testing Storage

**Test File:** `tests/backend/test_storage.py` (신규)

```python
import unittest
import os
from backend.app.storage import AnalysisStorage

class TestAnalysisStorage(unittest.TestCase):
    def setUp(self):
        self.db_path = ":memory:"  # In-memory DB for tests
        self.storage = AnalysisStorage(self.db_path)
    
    def test_save_and_get(self):
        analysis_id = self.storage.save(
            filename="test.txt",
            document_text="Some text",
            profile={"age": 22},
            extraction={"title": "Test"},
            eligibility={"status": "eligible"},
            warnings=[],
            checklist=[],
            actions=[]
        )
        
        result = self.storage.get(analysis_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["filename"], "test.txt")
        self.assertEqual(result["profile"]["age"], 22)
    
    def test_list_all(self):
        for i in range(3):
            self.storage.save(
                filename=f"test{i}.txt",
                document_text="Text",
                profile={},
                extraction={},
                eligibility={},
                warnings=[],
                checklist=[],
                actions=[]
            )
        
        analyses = self.storage.list_all()
        self.assertEqual(len(analyses), 3)
    
    def test_delete(self):
        analysis_id = self.storage.save(
            filename="test.txt",
            document_text="Text",
            profile={},
            extraction={},
            eligibility={},
            warnings=[],
            checklist=[],
            actions=[]
        )
        
        deleted = self.storage.delete(analysis_id)
        self.assertTrue(deleted)
        
        result = self.storage.get(analysis_id)
        self.assertIsNone(result)
```

**Run Tests:**
```bash
python -m unittest tests.backend.test_storage
```

---

## Part 3: Integration & Verification (1 hour)

### 3.1 Update `requirements.txt`

Add:
```
PyMuPDF==1.23.8
```

### 3.2 Run All Tests

```bash
python -m compileall backend scripts
python -m unittest discover -s tests -p "test_*.py"
node --check frontend/src/app.js
```

**Expected Result:** All tests pass ✅

### 3.3 Manual Verification

**Test 1: PDF Extraction**
```bash
python -c "
from backend.app.parser import extract_text_from_upload
# Create a simple text and see if it extracts
text = extract_text_from_upload('test.txt', b'Hello World')
print(text)
"
```

**Test 2: Storage Save/Load**
```bash
python -c "
from backend.app.storage import get_storage
storage = get_storage('test_demo.db')
id = storage.save(
    'test.txt', 'content', 
    {'age': 22}, {'title': 'Test'}, 
    {'status': 'eligible'}, [], [], []
)
result = storage.get(id)
print(f'Saved: {id}')
print(f'Retrieved: {result[\"filename\"]}')
"
```

**Test 3: API Endpoint (with running server)**
```bash
# Terminal 1:
python backend/run.py

# Terminal 2:
curl http://127.0.0.1:8000/api/analyses
# Should return: {"analyses": []}
```

### 3.4 Potential Issues & Solutions

| Issue | Solution |
|-------|----------|
| PyMuPDF install fails | `pip install --upgrade pip` 먼저 실행 |
| SQLite permission denied | 프로세스 리스타트 (파일 잠금 해제) |
| Test fails on Windows | `python -m unittest` 대신 `python -m pytest` 사용 (선택사항) |
| PDF with no text | Error message 반환 (자동 처리) |

---

## Deliverables (End of Day 1)

✅ **Completed:**
- [ ] `backend/app/parser.py` - PyMuPDF 통합
- [ ] `backend/app/storage.py` - SQLite 저장소 (신규)
- [ ] `backend/app/server.py` - 새 엔드포인트 추가
- [ ] `tests/backend/test_parser.py` - PDF 추출 테스트
- [ ] `tests/backend/test_storage.py` - 저장소 테스트
- [ ] `requirements.txt` - PyMuPDF 의존성 추가
- [ ] All tests passing

✅ **Not Done Yet (Day 2):**
- Frontend UI (히스토리, 저장 버튼)
- 샘플 데이터 3개
- Business Model 문서
- README 업데이트

---

## Next: Day 2 Frontend Implementation

After Day 1 is complete, proceed to `08-day2-frontend-and-docs.md`

