from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, load_only
from sqlalchemy.sql import func, select

from src.database import get_db
from src.models import note as models
from src.schemas import note as schemas

router = APIRouter(prefix='/notes', tags=['notes'])


@router.post(
    '/',
    response_model=schemas.NoteResponse,
    summary='Create a new note',
)
def create_note(data: schemas.NoteCreate, db: Session = Depends(get_db)):
    new_note = models.Note(
        title=data.title,
        content=data.content,
    )

    db.add(new_note)
    logger.debug(f"Adding note: '{new_note.title}'")
    try:
        db.commit()
        db.refresh(new_note)
    except IntegrityError:
        error_msg = 'Note with this title already exists.'
        logger.error(
            f"Error while creating note: '{new_note.title}'. {error_msg}"
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    except Exception as e:
        logger.error(f"Error while creating note: '{new_note.title}', {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return new_note


@router.get(
    '/',
    response_model=list[schemas.NoteList],
    summary='Get a list of all available notes.',
)
def get_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    I'm omitting the 'content' attribute to maximize query performance,
    since this endpoint will only be used to display the list of notes.
    """
    stmt = (
        select(models.Note)
        .options(
            load_only(
                models.Note.note_id,
                models.Note.title,
                models.Note.created_at,
                models.Note.updated_at,
            )
        )
        .offset(skip)
        .limit(limit)
    )

    total_records = db.scalar(select(func.count(models.Note.note_id)))
    logger.info(f'Total records: {total_records}')

    return db.scalars(stmt).all()


@router.get(
    '/{note_id}',
    response_model=schemas.NoteResponse,
    summary='Get informations about a specific note',
)
def get_note_by_id(note_id: int, db: Session = Depends(get_db)):
    stmt = select(models.Note).where(models.Note.note_id == note_id)
    note = db.scalar(stmt)

    if note is None:
        error_msg = 'Note is not found.'
        logger.error(
            f'Error while retrieving note: {note_id} (id). {error_msg}'
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg,
        )

    logger.info(f'Retrieving note: {note_id} (id).')
    return note


@router.patch(
    '/{note_id}',
    response_model=schemas.NoteResponse,
    summary='Partially updates information for a specific invoice',
)
def update_note(
    note_id: int, data: schemas.NoteUpdate, db: Session = Depends(get_db)
):
    stmt = select(models.Note).where(models.Note.note_id == note_id)
    note = db.scalar(stmt)

    if note is None:
        error_msg = 'Note is not found.'
        logger.error(
            f'Error while retrieving note: {note_id} (id). {error_msg}'
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg,
        )

    update_data = data.model_dump(exclude_unset=True)

    if 'title' in update_data:
        title = update_data['title']
        if not title.strip():
            error_msg = 'Title needs at least 1 character.'
            logger.error(
                f'Error while updating note: {note_id} (id). {error_msg}'
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

        title_stmt = select(models.Note).where(
            models.Note.title == title,
            models.Note.note_id != note_id,
        )
        existing_note = db.scalar(title_stmt)

        if existing_note:
            error_msg = 'Note with this title already exists.'
            logger.error(
                f'Error while updating note: {note_id} (id). {error_msg}'
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

    logger.info(f'The note with id = {note_id} was updated.')

    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)

    return note


@router.delete(
    '/{note_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deletes a specific note',
)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    stmt = select(models.Note).where(models.Note.note_id == note_id)
    note = db.scalar(stmt)

    if note is None:
        error_msg = 'Note is not found.'
        logger.error(
            f'Error while retrieving note: {note_id} (id). {error_msg}'
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg,
        )

    logger.info(f'Deleting note: {note_id} (id).')
    db.delete(note)
    db.commit()
