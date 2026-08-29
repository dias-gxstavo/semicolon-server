from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: str
    content: str


class NoteResponse(BaseModel):
    note_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
