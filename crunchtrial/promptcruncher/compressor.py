"""
promptcruncher — input-side prompt compression.
Strips tokens the model doesn't need before the API call.
"""

import re
from .rules import FILLER_PHRASES, FILLER_PATTERNS, REDUNDANT_OPENERS


class Compressor:
    def __init__(self, deduplicate=True, aggressive=False):
        """
        deduplicate: remove repeated sentences
        aggressive:  also strip hedging, softeners, and verbose transitions
        """
        self.deduplicate = deduplicate
        self.aggressive = aggressive

    def compress(self, text: str) -> str:
        text = self._strip_pleasantries(text)
        text = self._strip_filler_phrases(text)
        text = self._strip_redundant_openers(text)
        if self.aggressive:
            text = self._strip_hedging(text)
        if self.deduplicate:
            text = self._deduplicate_sentences(text)
        text = self._collapse_whitespace(text)
        return text.strip()

    def _strip_pleasantries(self, text: str) -> str:
        for phrase in FILLER_PHRASES:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            text = pattern.sub("", text)
        return text

    def _strip_filler_phrases(self, text: str) -> str:
        for pattern in FILLER_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text

    def _strip_redundant_openers(self, text: str) -> str:
        for pattern in REDUNDANT_OPENERS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text

    def _strip_hedging(self, text: str) -> str:
        hedges = [
            r"\bI was wondering if (you could )?(perhaps )?",
            r"\bwould you be able to\b",
            r"\bif (that'?s? )?okay( with you)?\b",
            r"\bif possible\b,?\s*",
            r"\bif you don'?t mind\b,?\s*",
            r"\bI hope this (isn'?t too much|makes sense|helps)\b[.,]?\s*",
            r"\bfeel free to\b",
            r"\bdon'?t hesitate to\b",
        ]
        for hedge in hedges:
            text = re.sub(hedge, "", text, flags=re.IGNORECASE)
        return text

    def _deduplicate_sentences(self, text: str) -> str:
        # Split into sentences, remove near-duplicates
        sentences = re.split(r'(?<=[.!?])\s+', text)
        seen = []
        result = []
        for sentence in sentences:
            normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
            normalized = re.sub(r'[^\w\s]', '', normalized)
            if not normalized:
                continue
            # Check for near-duplicates (simple word overlap)
            is_duplicate = False
            for s in seen:
                overlap = _word_overlap(normalized, s)
                if overlap > 0.85:
                    is_duplicate = True
                    break
            if not is_duplicate:
                seen.append(normalized)
                result.append(sentence)
        return ' '.join(result)

    def _collapse_whitespace(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' +\n', '\n', text)
        return text


def _word_overlap(a: str, b: str) -> float:
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)
