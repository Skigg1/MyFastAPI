from app.database import SessionLocal, engine
from app.models import Base, Genre, Movie
from sqlalchemy.orm import Session

def init_db():
    # 1. Сначала создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    # 2. Затем заполняем данными
    db = SessionLocal()
    
    try:
        # Создаем жанры
        genres = [
            Genre(name="Action", description="Exciting action movies"),
            Genre(name="Comedy", description="Funny movies"),
            Genre(name="Drama", description="Serious movies"),
        ]

        # Добавляем жанры в базу
        for genre in genres:
            db.add(genre)
        db.commit()  # Сохраняем жанры, чтобы получить их ID

        # Создаем фильмы
        movies = [
            Movie(
                title="The Shawshank Redemption",
                year=1994,
                duration=142,
                rating=9.3,
                description="Two imprisoned men bond over a number of years...",
                genres=[genres[2]]  # Drama
            ),
            Movie(
                title="The Dark Knight",
                year=2008,
                duration=152,
                rating=9.0,
                description="When the menace known as the Joker wreaks havoc...",
                genres=[genres[0], genres[2]]  # Action and Drama
            ),
        ]

        for movie in movies:
            db.add(movie)
        db.commit()
        
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Initial data has been added to the database.")