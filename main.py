from typing import Annotated, Literal, Union

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str = Field(
        default=None, title="name", description="The full name of the user"
    )


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(default=10, gt=1, le=100)
    offset: int = Field(
        default=0, ge=0, title="타이틀입니다.", description="디스크립션입니다."
    )
    order_by: Literal["name", "price"] = Field(
        default="name", description="Order by field"
    )
    tags: list[str] = []


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/items/")
async def create_item(item: Item):
    return item


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results
