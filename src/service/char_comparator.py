"""Символьный сравнитель."""

from typing import Optional
import re
import logging
from typing import List, Dict
from collections import Counter

from src.models import HorizontalProductLine, OutputCharComparator

logger = logging.getLogger(__name__)


class NotInputTextCharsError(ValueError):
    pass


class NotBaseTextCharsError(ValueError):
    pass


class NotInputTextError(ValueError):
    pass


class NotBaseTextError(ValueError):
    pass


class CharComparator:
    """
    Улучшенный символьный сравнитель:
    - нормализация текста
    - частотное сходство (cosine)
    - n-gram (bigrams) similarity (Dice)
    - LCS similarity (longest common subsequence)
    - Edit similarity (Levenshtein normalized)
    Итог — взвешенная сумма этих метрик (0..100).
    """

    def __init__(
        self,
        remove_punctuation: bool = True,
        remove_extra_spaces: bool = True,
        ngram_n: int = 2,
        weights: Optional[Dict[str, float]] = None,
    ):
        """
        weights keys: 'freq', 'ngram', 'lcs', 'edit' — значения суммируются до 1.0
        """
        self.remove_punctuation = remove_punctuation
        self.remove_extra_spaces = remove_extra_spaces
        self.ngram_n = ngram_n

        default = {"freq": 0.3, "ngram": 0.4, "lcs": 0.2, "edit": 0.1}
        if weights is None:
            weights = default
        # нормализация весов
        total = sum(weights.values())
        self.weights = {k: v / total for k, v in weights.items()}

    def search_sim(
        self,
        input_text: str,
        base_texts: List[HorizontalProductLine],
    ) -> OutputCharComparator:
        if not input_text:
            raise NotInputTextError("Input text is empty")

        if not base_texts:
            raise NotBaseTextError("Base texts are empty")

        input_norm = self._normalize_text(input_text)

        best_product: Optional[HorizontalProductLine] = None
        best_similarity: float = -1.0

        for product in base_texts:
            base_norm = self._normalize_text(product.product_name)

            similarity = self._combined_similarity(input_norm, base_norm)

            logger.debug(
                "Compared '%s' vs '%s' -> sim=%.4f", input_norm, base_norm, similarity
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_product = product

        if best_product is None:
            raise NotBaseTextError("No matching base text found")

        response = OutputCharComparator(
            input_text=input_text,
            horiazontal_product_line=best_product.index,
            similar_base_text=best_product.product_name,
            similarity_percent=round(best_similarity, 2),
        )

        print(response)
        return response

    # -----------------------
    # Normalization & utils
    # -----------------------
    def _normalize_text(self, text: str) -> str:
        if text is None:
            return ""
        t = text.lower()
        if self.remove_punctuation:
            # keep words/letters/digits and whitespace; supports unicode letters
            t = re.sub(r"[^\w\s]", "", t, flags=re.UNICODE)
        if self.remove_extra_spaces:
            t = re.sub(r"\s+", " ", t).strip()
        return t

    # -----------------------
    # Individual metrics
    # -----------------------
    @staticmethod
    def _char_freq_cosine(a: str, b: str) -> float:
        # Векторы частот символов -> косинусное сходство (0..100)
        ca = Counter(a)
        cb = Counter(b)
        if not ca or not cb:
            return 0.0
        # dot
        dot = sum(ca[ch] * cb.get(ch, 0) for ch in ca)
        norm_a = sum(v * v for v in ca.values()) ** 0.5
        norm_b = sum(v * v for v in cb.values()) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        cos = dot / (norm_a * norm_b)
        return cos * 100.0

    def _ngram_dice(self, a: str, b: str) -> float:
        # Counts-based Dice coefficient for n-grams (2*|A∩B|/(|A|+|B|))
        n = max(1, self.ngram_n)

        def ngrams(s: str):
            s_padded = s  # could pad with spaces if needed
            if len(s_padded) < n:
                return []
            return [s_padded[i : i + n] for i in range(len(s_padded) - n + 1)]

        na = Counter(ngrams(a))
        nb = Counter(ngrams(b))
        if not na or not nb:
            return 0.0
        common = sum(min(na[g], nb[g]) for g in na)
        total = sum(na.values()) + sum(nb.values())
        dice = (2.0 * common) / total
        return dice * 100.0

    @staticmethod
    def _lcs_similarity(a: str, b: str) -> float:
        # normalized length of LCS (longest common subsequence)
        if not a or not b:
            return 0.0
        la, lb = len(a), len(b)
        # DP matrix smaller dimension first to save memory
        dp = [0] * (lb + 1)
        for i in range(1, la + 1):
            prev = 0
            ai = a[i - 1]
            for j in range(1, lb + 1):
                temp = dp[j]
                if ai == b[j - 1]:
                    dp[j] = prev + 1
                else:
                    dp[j] = max(dp[j], dp[j - 1])
                prev = temp
        lcs_len = dp[lb]
        denom = max(la, lb)
        return (lcs_len / denom) * 100.0

    @staticmethod
    def _levenshtein_similarity(a: str, b: str) -> float:
        # normalized Levenshtein similarity: (1 - distance / max_len) * 100
        if a == b:
            return 100.0
        if not a or not b:
            return 0.0
        la, lb = len(a), len(b)
        if la < lb:
            # swap to ensure la >= lb to reduce memory
            a, b = b, a
            la, lb = lb, la
        previous = list(range(lb + 1))
        for i, ca in enumerate(a, start=1):
            current = [i] + [0] * lb
            for j, cb in enumerate(b, start=1):
                insertions = previous[j] + 1
                deletions = current[j - 1] + 1
                substitutions = previous[j - 1] + (0 if ca == cb else 1)
                current[j] = min(insertions, deletions, substitutions)
            previous = current
        dist = previous[lb]
        max_len = max(len(a), len(b))
        sim = max(0.0, 1.0 - dist / max_len)
        return sim * 100.0

    # -----------------------
    # Combined similarity
    # -----------------------
    def _combined_similarity(self, a: str, b: str) -> float:
        """
        Возвращает значение 0..100 как взвешенную сумму метрик.
        """
        if not a or not b:
            return 0.0

        freq = self._char_freq_cosine(a, b)
        ngram = self._ngram_dice(a, b)
        lcs = self._lcs_similarity(a, b)
        edit = self._levenshtein_similarity(a, b)

        w = self.weights
        combined = (
            w.get("freq", 0) * freq
            + w.get("ngram", 0) * ngram
            + w.get("lcs", 0) * lcs
            + w.get("edit", 0) * edit
        )
        # Clamp 0..100
        return max(0.0, min(100.0, combined))
