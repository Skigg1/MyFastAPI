from fastapi import FastAPI, Query, Path, HTTPException, status
from pydantic import BaseModel, Field, confloat, conint, constr
from typing import Optional, List
from uuid import uuid4

app = FastAPI()


# Модель для хранения товаров
class Item(BaseModel):
    id: str
    name: str
    price: float
    description: Optional[str] = None


class ItemCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Smartphone",
        description="Item name (2-100 characters)",
    )
    price: float = Field(
        ..., gt=0, example=499.99, description="Item price (must be positive)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        example="Latest model with advanced features",
        description="Optional item description (max 500 characters)",
    )


# "База данных" товаров
fake_items_db = [
    Item(id=str(uuid4()), name="Smartphone", price=499.99, description="Latest model"),
    Item(id=str(uuid4()), name="Laptop", price=999.99, description="Powerful laptop"),
    Item(id=str(uuid4()), name="Tablet", price=299.99),
    Item(id=str(uuid4()), name="Headphones", price=149.99),
    Item(id=str(uuid4()), name="Smartwatch", price=199.99),
]


@app.get("/items/", response_model=List[Item])
async def get_items(
    name: Optional[str] = Query(
        None,
        min_length=2,
        description="Filter items by name (min 2 chars)",
        example="phone",
    ),
    min_price: Optional[float] = Query(
        None, gt=0, description="Minimum price (must be positive)", example=100
    ),
    max_price: Optional[float] = Query(
        None,
        gt=0,
        description="Maximum price (must be greater than min_price)",
        example=1000,
    ),
    limit: Optional[int] = Query(
        10, ge=1, le=100, description="Number of items to return (1-100)", example=5
    ),
):
    """
    Get a list of items with optional filtering by name and price range.

    - **name**: Filter by item name (min 2 characters)
    - **min_price**: Minimum item price
    - **max_price**: Maximum item price (must be > min_price)
    - **limit**: Number of items to return (default: 10, max: 100)
    """
    if min_price is not None and max_price is not None and max_price <= min_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="max_price must be greater than min_price",
        )

    filtered_items = fake_items_db

    if name:
        filtered_items = [
            item for item in filtered_items if name.lower() in item.name.lower()
        ]

    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]

    return filtered_items[:limit]


@app.get("/items/{item_id}", response_model=Item)
async def get_item(
    item_id: str = Path(..., description="The ID of the item to get", example="42")
):
    """
    Get information about a specific item by its ID.

    - **item_id**: The ID of the item to retrieve
    """
    for item in fake_items_db:
        if item.id == item_id:
            return item

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """
    Create a new item with the given information.

    - **name**: Item name (2-100 characters)
    - **price**: Item price (must be > 0)
    - **description**: Optional item description (max 500 characters)
    """
    new_item = Item(
        id=str(uuid4()), name=item.name, price=item.price, description=item.description
    )
    fake_items_db.append(new_item)
    return new_item
