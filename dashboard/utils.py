from __future__ import annotations
import re
import uuid
from datetime import datetime, timezone
from typing import Optional


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_drive_link(url: str) -> bool:
    pattern = r"^https://(drive|docs)\.google\.com/.*$"
    return re.match(pattern, url) is not None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        from io import BytesIO
        try:
            # Primary parser
            from PyPDF2 import PdfReader as _PdfReader  # type: ignore
        except ImportError:
            try:
                # Fallback parser if installed under alternate name
                from pypdf import PdfReader as _PdfReader  # type: ignore
            except Exception as e:
                return f"PDF parsing failed: missing PDF parser ({e})"
        reader = _PdfReader(BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts).strip()
    except Exception as e:
        return f"PDF parsing failed: {e}"
