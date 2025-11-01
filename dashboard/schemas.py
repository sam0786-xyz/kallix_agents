from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, EmailStr


class ContactInfo(BaseModel):
    email: str
    phone: str


class ClientBusinessDetails(BaseModel):
    client_id: str
    business_name: str
    business_description: str
    industry: str
    contact_info: ContactInfo


KBType = Literal["txt", "pdf", "drive_link", "custom_text"]


class KnowledgeBaseEntry(BaseModel):
    kb_entry_id: str
    client_id: str
    type: KBType
    value: str
    created_at: str  # ISO8601 timestamp


class CallRecord(BaseModel):
    call_id: str
    client_id: str
    timestamp: str  # ISO8601 timestamp
    agent_id: str
    callee: str
    transcript: str
    audio_url: str
    call_status: Literal["completed", "failed"]
    error_message: Optional[str]


class ToolActionEvent(BaseModel):
    action_id: str
    client_id: str
    action_type: Literal[
        "email",
        "brochure",
        "calendar_booking",
        "sheet_update",
        "crm_update",
    ]
    status: Literal["success", "failed"]
    error_message: Optional[str]
    timestamp: str  # ISO8601 timestamp


class PaginatedResponse(BaseModel):
    items: list
    page: int
    per_page: int
    total_items: int
    sort_by: Optional[str] = None
    sort_order: Optional[Literal["asc", "desc"]] = None

