from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models
from app.endpoints import movies, genres
from app import schemas
from app import crud

# Создаем главный роутер для основных эндпоинтов
main_router = APIRouter()


@main_router.get("/", tags=["root"])
def read_root():
    """Главная страница API"""
    return {"message": "Welcome to Filmoteka API"}


@main_router.post(
    "/register",
    response_model=schemas.User,
    status_code=201,
    tags=["authentication"],
    summary="Register new user",
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя

    - **username**: Логин пользователя
    - **password**: Пароль (минимум 6 символов)
    """
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


# Инициализация FastAPI приложения
app = FastAPI(
    title="Filmoteka API",
    version="1.0.0",
    description="API для управления фильмотекой",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключение всех роутеров
app.include_router(main_router)
app.include_router(movies.router)
app.include_router(genres.router)

# Создание таблиц в базе данных
models.Base.metadata.create_all(bind=engine)
