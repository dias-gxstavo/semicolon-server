from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from .database import engine, get_db
from .models import note
from .routers import notes

note.Base.metadata.create_all(bind=engine)
app = FastAPI(title='semicolon - a simple markdown editor')

app.include_router(notes.router)


@app.get('/health', status_code=status.HTTP_200_OK, tags=['health'])
async def health_check(db: Session = Depends(get_db)):
    """
    Returns the status of the database connection
    """
    try:
        db.execute(text('SELECT 1'))
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'Database connection failed: {str(e)}',
        )
