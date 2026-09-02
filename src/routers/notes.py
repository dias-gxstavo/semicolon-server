from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import note as models
from src.schemas import note as schemas

router = APIRouter(prefix='/notes', tags=['notes'])


@router.post('/', response_model=schemas.NoteResponse)
def create_note(data: schemas.NoteCreate, db: Session = Depends(get_db)):
    new_note = models.Note(
        title=data.title,
        content=data.content,
    )

    db.add(new_note)
    try:
        db.commit()
        db.refresh(new_note)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Note with this title already exists.',
        )
    return new_note


@router.get('/', response_model=list[schemas.NoteList])
def get_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    stmt = db.query(
        models.Note.note_id,
        models.Note.title,
        models.Note.created_at,
        models.Note.updated_at,
    ).offset(skip).limit(limit)
    return stmt


@router.get('/{note_id}', response_model=schemas.NoteResponse)
def get_note_by_id(note_id: int, db: Session = Depends(get_db)):
    stmt = db.query(models.Note).filter(models.Note.note_id == note_id).first()

    if stmt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Note is not found.'
        )

    return stmt


@router.patch('/{note_id}', response_model=schemas.NoteResponse)
def update_note(
    note_id: int, data: schemas.NoteUpdate, db: Session = Depends(get_db)
):

    note = db.query(models.Note).filter(models.Note.note_id == note_id).first()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Note is not found.'
        )

    update_data = data.model_dump(exclude_unset=True)

    if 'title' in update_data:
        existing_note = (
            db.query(models.Note)
            .filter(
                models.Note.title == update_data['title'],
                models.Note.note_id != note_id,
            )
            .first()
        )

        if existing_note:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Note with this title already exists.',
            )

    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)

    return note


@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    stmt = db.query(models.Note).filter(models.Note.note_id == note_id).first()

    if stmt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Note is not found.'
        )

    db.delete(stmt)
    db.commit()
