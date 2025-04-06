from typing import Union
import random
import math

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/about")
def read_root():
    return {"Разработчик": "Соловьев Александр", "Студент группы": "ИСТ-233902у"}


@app.get("/rnd")
async def random_number():
    """Возвращает случайное число от 1 до 10"""
    return {"random_number": random.randint(1, 10)}


@app.get("/t_square")
def triangle_square(a: float, b: float, c: float):

    if not (a + b > c and a + c > b and b + c > a):
        return {"Треугольник с такими сторонами не существует"}

    perimeter = a + b + c
    p = perimeter / 2
    area = math.sqrt(p * (p - a) * (p - b) * (p - c))

    return {
        "Периметр": round(perimeter, 2),
        "Площадь": round(area, 2),
    }
