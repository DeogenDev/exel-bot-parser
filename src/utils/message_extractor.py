import logging
import re
from flag import dflagize

from src.models import ExtractMessage, ProductCount

logger = logging.getLogger(__name__)


class MessageExtractError(ValueError):
    pass


class MessageExtractNoName(ValueError):
    pass


class ProductExtractError(ValueError):
    pass


class MessageExtractor:
    BUYER_NAME_PATTERN = re.compile(
        r"^заказ\s+\d+\s*\n\s*(.+?)\s*(?=\n|$)", re.MULTILINE | re.IGNORECASE
    )
    PRODUCT_PATTERN = re.compile(
        r"^\s*(.+)(?:\s+[\d.,]+(?:\s*[₽$€£р.\u0440\u0443\u0431]*)?)?\s*-\s*\(?(\d+)\s*(?:шт)?\)?\s*$"
    )
    FLAG_COLONS_PATTERN = re.compile(r":([A-Z]{2}):")

    def extract_message(self, text: str) -> ExtractMessage:
        normalized_text = dflagize(text)

        buyer_name = self._extract_buyer_name(text)
        if buyer_name == "Неизвестный":
            raise MessageExtractNoName("Не удалось распознать покупателя.")

        products_text = self._get_products_text(normalized_text)
        if not products_text:
            raise MessageExtractError("Не удалось распознать товары.")

        products, errors_products = self._extract_products(products_text)

        if not products:
            raise MessageExtractError("Не удалось распознать товары.")

        return ExtractMessage(
            buyer_name=buyer_name,
            products=products,
            errors_products=errors_products,
        )

    def _extract_buyer_name(self, text: str) -> str:
        match = self.BUYER_NAME_PATTERN.search(text.strip())
        return match.group(1).strip() if match else "Неизвестный"

    def _extract_products(self, text: str) -> tuple[list[ProductCount], list[str]]:
        products: list[ProductCount] = []
        errors_products: list[str] = []

        for line in text.splitlines():
            match = self.PRODUCT_PATTERN.match(line)
            if not match:
                logger.warning("Строка не соответствует шаблону: %s", line)
                errors_products.append(line)
                continue

            try:
                name_raw, count_str = match.groups()
                products.append(
                    ProductCount(
                        name=self._normalize_flag_code(name_raw),
                        count=int(count_str),
                    )
                )
            except Exception:
                logger.exception("Не удалось распознать товар: %s", line)
                errors_products.append(line)
                continue

        return products, errors_products

    def _normalize_flag_code(self, name: str) -> str:
        return self.FLAG_COLONS_PATTERN.sub(r"\1", name).strip()

    def _get_products_text(self, text: str) -> str:
        buyer_match = self.BUYER_NAME_PATTERN.search(text)
        if not buyer_match:
            return ""
        products_part = text[buyer_match.end() :].strip()

        return "\n".join(line for line in products_part.splitlines() if line.strip())


messages_extractor = MessageExtractor()
