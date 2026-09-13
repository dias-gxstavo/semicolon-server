from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from .database import engine, get_db
from .models import note
from .routers import notes

note.Base.metadata.create_all(bind=engine)
app = FastAPI(title='semicolon - a simple markdown editor')

app.include_router(notes.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get(
    '/health',
    status_code=status.HTTP_200_OK,
    tags=['health'],
    summary='Returns the status of the database connection',
)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'Database connection failed: {str(e)}',
        )
