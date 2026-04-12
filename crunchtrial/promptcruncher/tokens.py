"""
Token counting for promptcruncher.
Uses tiktoken if available and cached locally, otherwise falls back to
a word-based estimate (~1.3 tokens/word) that requires no network access.
"""

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False

_tiktoken_encoder = None


def _get_encoder(model: str):
    """Lazy-load tiktoken encoder. Returns None if unavailable or requires network."""
    global _tiktoken_encoder
    if not _TIKTOKEN_AVAILABLE:
        return None
    if _tiktoken_encoder is not None:
        return _tiktoken_encoder
    try:
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        _tiktoken_encoder = enc
        return enc
    except Exception:
        return None


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count tokens in text.
    Uses tiktoken if available and cached, otherwise estimates from word count.
    """
    enc = _get_encoder(model)
    if enc is not None:
        return len(enc.encode(text))
    return int(len(text.split()) * 1.3)


def compression_stats(original: str, compressed: str, model: str = "gpt-4o") -> dict:
    """
    Return a dict with token counts and savings.
    """
    original_tokens = count_tokens(original, model)
    compressed_tokens = count_tokens(compressed, model)
    saved = original_tokens - compressed_tokens
    ratio = (saved / original_tokens * 100) if original_tokens > 0 else 0

    return {
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "tokens_saved": saved,
        "compression_ratio": round(ratio, 1),
        "tiktoken_available": _TIKTOKEN_AVAILABLE,
    }
