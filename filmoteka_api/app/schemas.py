from typing import List, Optional
from pydantic import BaseModel, validator, constr, conint, confloat
from datetime import datetime


class GenreBase(BaseModel):
    name: str
    description: Optional[str] = None


class GenreCreate(GenreBase):
    pass


class Genre(GenreBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class MovieBase(BaseModel):
    title: str
    year: Optional[int] = None
    duration: Optional[int] = None  # в минутах
    rating: Optional[float] = None  # от 0 до 10
    description: Optional[str] = None
    poster_url: Optional[str] = None
    genre_ids: List[int] = []

    @validator("year")
    def validate_year(cls, v):
        if v is not None and (v < 1895 or v > datetime.now().year + 2):
            raise ValueError(f"Year must be between 1895 and {datetime.now().year + 2}")
        return v

    @validator("rating")
    def validate_rating(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError("Rating must be between 0 and 10")
        return v

    @validator("duration")
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Duration must be positive")
        return v


class MovieCreate(MovieBase):
    pass


class MovieUpdate(MovieBase):
    title: Optional[str] = None


class Movie(MovieBase):
    id: int
    created_at: datetime
    genres: List[Genre] = []

    class Config:
        from_attributes = True
