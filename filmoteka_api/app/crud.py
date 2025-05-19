from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_genre(db: Session, genre_id: int):
    return db.query(models.Genre).filter(models.Genre.id == genre_id).first()


def get_genre_by_name(db: Session, name: str):
    return db.query(models.Genre).filter(models.Genre.name == name).first()


def get_genres(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Genre).offset(skip).limit(limit).all()


def create_genre(db: Session, genre: schemas.GenreCreate):
    db_genre = models.Genre(name=genre.name, description=genre.description)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def get_movies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Movie).offset(skip).limit(limit).all()


def create_movie(db: Session, movie: schemas.MovieCreate):
    # Получаем жанры по их ID
    genres = db.query(models.Genre).filter(models.Genre.id.in_(movie.genre_ids)).all()

    db_movie = models.Movie(
        title=movie.title,
        year=movie.year,
        duration=movie.duration,
        rating=movie.rating,
        description=movie.description,
        poster_url=movie.poster_url,
        genres=genres,
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie(db: Session, movie_id: int, movie: schemas.MovieUpdate):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return None

    if movie.title is not None:
        db_movie.title = movie.title
    if movie.year is not None:
        db_movie.year = movie.year
    if movie.duration is not None:
        db_movie.duration = movie.duration
    if movie.rating is not None:
        db_movie.rating = movie.rating
    if movie.description is not None:
        db_movie.description = movie.description
    if movie.poster_url is not None:
        db_movie.poster_url = movie.poster_url
    if movie.genre_ids:
        genres = (
            db.query(models.Genre).filter(models.Genre.id.in_(movie.genre_ids)).all()
        )
        db_movie.genres = genres

    db.commit()
    db.refresh(db_movie)
    return db_movie


def delete_movie(db: Session, movie_id: int):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return False
    db.delete(db_movie)
    db.commit()
    return True
