from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .schemas import (
    ClientBusinessDetails,
    KnowledgeBaseEntry,
    CallRecord,
    ToolActionEvent,
)

DATA_DIR = Path(__file__).parent / "data"
CLIENTS_FILE = DATA_DIR / "clients.json"
KB_FILE = DATA_DIR / "kb_entries.json"
CALLS_FILE = DATA_DIR / "calls.json"
ACTIONS_FILE = DATA_DIR / "actions.json"


def _ensure_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for f in [CLIENTS_FILE, KB_FILE, CALLS_FILE, ACTIONS_FILE]:
        if not f.exists():
            f.write_text(json.dumps({"items": []}, indent=2))


def _read_items(path: Path) -> List[Dict[str, Any]]:
    _ensure_files()
    data = json.loads(path.read_text() or "{}")
    return data.get("items", [])


def _write_items(path: Path, items: List[Dict[str, Any]]) -> None:
    path.write_text(json.dumps({"items": items}, indent=2))


def upsert_client(details: ClientBusinessDetails) -> Dict[str, Any]:
    items = _read_items(CLIENTS_FILE)
    existing_idx = next((i for i, it in enumerate(items) if it["client_id"] == details.client_id), None)
    if existing_idx is not None:
        items[existing_idx] = details.model_dump()
    else:
        items.append(details.model_dump())
    _write_items(CLIENTS_FILE, items)
    return details.model_dump()


def list_clients(page: int = 1, per_page: int = 10, sort_by: Optional[str] = None, sort_order: Optional[str] = "asc") -> Dict[str, Any]:
    items = _read_items(CLIENTS_FILE)
    if sort_by:
        items.sort(key=lambda x: (x.get(sort_by) or ""))
        if sort_order == "desc":
            items.reverse()
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total_items": total,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }


def add_kb_entry(entry: KnowledgeBaseEntry) -> Dict[str, Any]:
    items = _read_items(KB_FILE)
    items.append(entry.model_dump())
    _write_items(KB_FILE, items)
    return entry.model_dump()


def list_kb_entries(
    client_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
) -> Dict[str, Any]:
    items = _read_items(KB_FILE)
    if client_id:
        items = [it for it in items if it.get("client_id") == client_id]
    if sort_by:
        items.sort(key=lambda x: (x.get(sort_by) or ""))
        if sort_order == "desc":
            items.reverse()
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total_items": total,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }


def add_call_record(record: CallRecord) -> Dict[str, Any]:
    items = _read_items(CALLS_FILE)
    items.append(record.model_dump())
    _write_items(CALLS_FILE, items)
    return record.model_dump()


def list_call_records(
    client_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    call_status: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: Optional[str] = "timestamp",
    sort_order: Optional[str] = "desc",
) -> Dict[str, Any]:
    items = _read_items(CALLS_FILE)
    if client_id:
        items = [it for it in items if it.get("client_id") == client_id]
    if agent_id:
        items = [it for it in items if it.get("agent_id") == agent_id]
    if call_status:
        items = [it for it in items if it.get("call_status") == call_status]
    if sort_by:
        items.sort(key=lambda x: (x.get(sort_by) or ""))
        if sort_order == "desc":
            items.reverse()
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total_items": total,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }


def add_tool_action(event: ToolActionEvent) -> Dict[str, Any]:
    items = _read_items(ACTIONS_FILE)
    items.append(event.model_dump())
    _write_items(ACTIONS_FILE, items)
    return event.model_dump()


def list_tool_actions(
    client_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: Optional[str] = "timestamp",
    sort_order: Optional[str] = "desc",
) -> Dict[str, Any]:
    items = _read_items(ACTIONS_FILE)
    if client_id:
        items = [it for it in items if it.get("client_id") == client_id]
    if sort_by:
        items.sort(key=lambda x: (x.get(sort_by) or ""))
        if sort_order == "desc":
            items.reverse()
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total_items": total,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

