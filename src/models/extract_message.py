"""Модель извлеченных данных."""

from pydantic import BaseModel
from typing import List
from pydantic import Field


class ProductCount(BaseModel):
    name: str = Field(..., description="Название товара")
    count: int = Field(..., ge=0, description="Количество")


class ExtractMessage(BaseModel):
    buyer_name: str
    products: List[ProductCount] = Field(..., min_items=1)
    errors_products: List[str]
