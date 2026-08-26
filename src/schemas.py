from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str


class UserResponse(BaseModel):
    note_id: int
    title: str
    content: str

    class Config:
        orm_mode = True
