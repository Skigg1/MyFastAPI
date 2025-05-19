from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas, crud
from ..auth import get_current_user

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", response_model=List[schemas.Genre])
def read_genres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    genres = crud.get_genres(db, skip=skip, limit=limit)
    return genres


@router.post("/", response_model=schemas.Genre, status_code=status.HTTP_201_CREATED)
def create_genre(
    genre: schemas.GenreCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_genre = crud.get_genre_by_name(db, name=genre.name)
    if db_genre:
        raise HTTPException(status_code=400, detail="Genre already exists")
    return crud.create_genre(db=db, genre=genre)
