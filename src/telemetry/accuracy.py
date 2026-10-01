import re
from typing import Dict


class AccuracyEvaluator:
    """Calculates Word Error Rate (WER) for English/Indonesian and Character Error Rate (CER) for Mandarin Chinese."""

    @staticmethod
    def normalize_text(text: str, language: str = "en") -> str:
        """Standardize text by lowercasing and stripping punctuation."""
        text = text.lower()
        # Remove punctuation except whitespace
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def calculate_wer(cls, reference: str, hypothesis: str, language: str = "en") -> float:
        ref = cls.normalize_text(reference, language=language)
        hyp = cls.normalize_text(hypothesis, language=language)

        ref_words = ref.split()
        hyp_words = hyp.split()

        if not ref_words:
            return 0.0 if not hyp_words else 1.0

        # Dynamic programming Levenshtein distance
        d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
        for i in range(len(ref_words) + 1):
            d[i][0] = i
        for j in range(len(hyp_words) + 1):
            d[0][j] = j

        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i - 1] == hyp_words[j - 1]:
                    d[i][j] = d[i - 1][j - 1]
                else:
                    d[i][j] = min(
                        d[i - 1][j] + 1,      # deletion
                        d[i][j - 1] + 1,      # insertion
                        d[i - 1][j - 1] + 1   # substitution
                    )
        return float(d[len(ref_words)][len(hyp_words)]) / float(len(ref_words))

    @classmethod
    def calculate_cer(cls, reference: str, hypothesis: str) -> float:
        """Calculate Character Error Rate for Mandarin Chinese."""
        ref = cls.normalize_text(reference, language="zh").replace(" ", "")
        hyp = cls.normalize_text(hypothesis, language="zh").replace(" ", "")

        if not ref:
            return 0.0 if not hyp else 1.0

        ref_chars = list(ref)
        hyp_chars = list(hyp)

        d = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
        for i in range(len(ref_chars) + 1):
            d[i][0] = i
        for j in range(len(hyp_chars) + 1):
            d[0][j] = j

        for i in range(1, len(ref_chars) + 1):
            for j in range(1, len(hyp_chars) + 1):
                if ref_chars[i - 1] == hyp_chars[j - 1]:
                    d[i][j] = d[i - 1][j - 1]
                else:
                    d[i][j] = min(
                        d[i - 1][j] + 1,
                        d[i][j - 1] + 1,
                        d[i - 1][j - 1] + 1
                    )
        return float(d[len(ref_chars)][len(hyp_chars)]) / float(len(ref_chars))
