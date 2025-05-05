from fastapi import FastAPI
from app.endpoints import movies, genres
from fastapi.staticfiles import StaticFiles
from .database import engine
from . import models
from .endpoints import movies, genres

# Создание таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(movies.router)
app.include_router(genres.router)

app = FastAPI(title="Filmoteka API", version="1.0.0")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(movies.router)
app.include_router(genres.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Filmoteka API"}
