"""Модели похожести."""

from pydantic import BaseModel


class OutputCharComparator(BaseModel):
    """Модель похожести слов."""

    input_text: str

    horiazontal_product_line: int
    similar_base_text: str
    similarity_percent: float
