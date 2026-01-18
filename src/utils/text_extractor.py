import logging
import re
from flag import dflagize

from src.models import ExtractMessage, ProductCount

logger = logging.getLogger(__name__)


class TextExtractor:
    BUYER_NAME_PATTERN = re.compile(
        r"^Заказ \d+\s*\n(.+?)(?=\n[A-Z]|$)",
        re.MULTILINE,
    )

    PRODUCT_PATTERN = re.compile(r"^\s*(.+?)\s*-\s*(\d+)\s*$")

    FLAG_COLONS_PATTERN = re.compile(r":([A-Z]{2}):")

    def extract_message(self, text: str) -> ExtractMessage:
        try:
            normalized_text = dflagize(text)

            buyer_name = self._extract_buyer_name(text)
            products = self._extract_products(normalized_text)

            return ExtractMessage(
                buyer_name=buyer_name,
                products=products,
            )
        except Exception as e:
            print(e)
            return ExtractMessage(
                buyer_name="Неизвестный",
                products=[],
            )

    def _extract_buyer_name(self, text: str) -> str:
        match = self.BUYER_NAME_PATTERN.search(text.strip())
        return match.group(1).strip() if match else "Неизвестный"

    def _extract_products(self, text: str) -> list[ProductCount]:
        products: list[ProductCount] = []

        for line in text.splitlines():
            match = self.PRODUCT_PATTERN.match(line)
            if not match:
                continue

            name_raw, count_str = match.groups()
            products.append(
                ProductCount(
                    name=self._normalize_flag_code(name_raw),
                    count=int(count_str),
                )
            )

        return products

    def _normalize_flag_code(self, name: str) -> str:
        return self.FLAG_COLONS_PATTERN.sub(r"\1", name).strip()
