from typing import List
from pydantic import BaseModel, Field


class HorizontalProductLine(BaseModel):
    """Товар с индексом колонки в таблице."""

    product_name: str = Field(..., description="Название товара")
    index: int = Field(..., description="Индекс колонки")


class InsertData(BaseModel):
    """Данные для вставки в ячейку Excel."""

    x_index: str = Field(..., description="Буква колонки (A, B, C...)")
    y_index: int = Field(..., description="Номер строки")
    value: str | int | float = Field(..., description="Значение для вставки")


class InputProducts(BaseModel):
    """Входные данные для заполнения таблицы товаров."""

    buyer_name: str = Field(..., description="Имя покупателя")
    insert_data: List[InsertData] = Field(
        ..., min_items=1, description="Список ячеек для заполнения"
    )
