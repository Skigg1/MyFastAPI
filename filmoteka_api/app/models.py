from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Table,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


# Таблица для связи многие-ко-многим между фильмами и жанрами
movie_genre_association = Table(
    "movie_genre_association",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column("genre_id", Integer, ForeignKey("genres.id")),
)


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    movies = relationship(
        "Movie", secondary=movie_genre_association, back_populates="genres"
    )


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    year = Column(Integer)
    duration = Column(Integer)  # в минутах
    rating = Column(Float)  # от 0 до 10
    description = Column(String)
    poster_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    genres = relationship(
        "Genre", secondary=movie_genre_association, back_populates="movies"
    )
