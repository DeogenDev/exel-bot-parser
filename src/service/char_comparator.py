"""Символьный сравнитель."""

from typing import List, Dict
from collections import Counter

from src.models import HorizontalProductLine, OutputCharComparator


class NotInputTextCharsError(ValueError):
    pass


class NotBaseTextCharsError(ValueError):
    pass


class NotInputTextError(ValueError):
    pass


class NotBaseTextError(ValueError):
    pass


class CharComparator:
    """Символьный сравнитель на основе частот символов."""

    def search_sim(
        self,
        input_text: str,
        base_texts: List[HorizontalProductLine],
    ) -> OutputCharComparator:
        if not input_text:
            raise NotInputTextError("Input text is empty")

        if not base_texts:
            raise NotBaseTextError("Base texts are empty")

        input_chars = self._text_to_char_stats(input_text)

        best_product: HorizontalProductLine | None = None
        best_similarity: float = -1.0

        for product in base_texts:
            base_chars = self._text_to_char_stats(product.product_name)

            similarity = self._calculate_similarity(
                input_chars=input_chars,
                base_chars=base_chars,
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_product = product

        if best_product is None:
            raise NotBaseTextError("No matching base text found")

        return OutputCharComparator(
            input_text=input_text,
            horiazontal_product_line=best_product.index,
            similar_base_text=best_product.product_name,
            similarity_percent=round(best_similarity, 2),
        )

    @staticmethod
    def _text_to_char_stats(text: str) -> Dict[str, int]:
        chars = dict(Counter(text.lower()))
        if not chars:
            raise NotInputTextCharsError("Text chars are empty")
        return chars

    @staticmethod
    def _calculate_similarity(
        input_chars: Dict[str, int],
        base_chars: Dict[str, int],
    ) -> float:
        """
        Частотное сходство символов (percentage).
        """

        if not input_chars:
            raise NotInputTextCharsError("Input text chars are empty")

        if not base_chars:
            raise NotBaseTextCharsError("Base text chars are empty")

        common_weight = sum(
            min(input_chars.get(ch, 0), count) for ch, count in base_chars.items()
        )

        base_weight = sum(base_chars.values())

        return (common_weight / base_weight) * 100
