from fastapi import HTTPException, status
from sqlalchemy import select

from src.database import SessionLocal
from src.models import note as models


def seed_database():
    with SessionLocal.begin() as db:
        note = models.Note(title='Introdução', content="""\n# Bem vindo(a) ao semicolon!\n\nO semicolon surgiu como um editor rápido pra arquivos pessoais em **.md**. Aliás, o tema do editor é inspirado no [Catpuccin Mocha](https://catppuccin.com/palette/)\n\n![welcome](https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWdzem1mYWhvZzNwZXl2bzNueGloZ29ybGpxNzhiaDNwbWVkOXFnYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ASd0Ukj0y3qMM/giphy.gif)\n\nSinta-se a vontade para explorar o editor.""")

        stmt = db.scalar(
            select(models.Note).where(models.Note.title == note.title)
        )

        if stmt:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Note with this title already exists.',
            )

        db.add(note)
