from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from .database import engine, get_db
from .models import note

note.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get('/health', status_code=status.HTTP_200_OK, tags=['health'])
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'Database connection failed: {str(e)}',
        )
