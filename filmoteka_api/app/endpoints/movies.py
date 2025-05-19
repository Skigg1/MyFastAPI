from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from ..database import get_db
from .. import schemas, crud
from ..auth import get_current_user

router = APIRouter(prefix="/movies", tags=["movies"])

# Настройки для загрузки файлов
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
POSTERS_DIR = "app/static/posters"

# Создаем директорию для постеров, если ее нет
os.makedirs(POSTERS_DIR, exist_ok=True)


@router.get("/", response_model=List[schemas.Movie])
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movies = crud.get_movies(db, skip=skip, limit=limit)
    return movies


@router.get("/{movie_id}", response_model=schemas.Movie)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie


@router.post("/", response_model=schemas.Movie, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie: schemas.MovieCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    # Проверяем, что все указанные жанры существуют
    for genre_id in movie.genre_ids:
        if not crud.get_genre(db, genre_id):
            raise HTTPException(
                status_code=400, detail=f"Genre with id {genre_id} not found"
            )

    return crud.create_movie(db=db, movie=movie)


@router.put("/{movie_id}", response_model=schemas.Movie)
def update_movie(
    movie_id: int,
    movie: schemas.MovieUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Проверяем, что все указанные жанры существуют
    if movie.genre_ids:
        for genre_id in movie.genre_ids:
            if not crud.get_genre(db, genre_id):
                raise HTTPException(
                    status_code=400, detail=f"Genre with id {genre_id} not found"
                )

    return crud.update_movie(db=db, movie_id=movie_id, movie=movie)


@router.put("/{movie_id}/image", response_model=schemas.Movie)
async def update_movie_image(
    movie_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    # Проверяем тип файла
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not supported. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    # Проверяем размер файла
    file.file.seek(0, 2)  # Перемещаем указатель в конец файла
    file_size = file.file.tell()
    file.file.seek(0)  # Возвращаем указатель в начало

    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {MAX_IMAGE_SIZE / 1024 / 1024}MB",
        )

    # Генерируем уникальное имя файла
    file_ext = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(POSTERS_DIR, new_filename)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Обновляем URL постера в базе данных
    poster_url = f"/static/posters/{new_filename}"
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        # Удаляем сохраненный файл, если фильм не найден
        os.remove(file_path)
        raise HTTPException(status_code=404, detail="Movie not found")

    # Удаляем старый постер, если он существует
    if db_movie.poster_url:
        old_poster_path = os.path.join(
            POSTERS_DIR, os.path.basename(db_movie.poster_url)
        )
        if os.path.exists(old_poster_path):
            os.remove(old_poster_path)

    db_movie.poster_url = poster_url
    db.commit()
    db.refresh(db_movie)

    return db_movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Удаляем постер, если он существует
    if db_movie.poster_url:
        poster_path = os.path.join(POSTERS_DIR, os.path.basename(db_movie.poster_url))
        if os.path.exists(poster_path):
            os.remove(poster_path)

    crud.delete_movie(db=db, movie_id=movie_id)
    return None
