"""
promptcruncher — compress your prompts before sending them to an LLM.
Removes tokens the model doesn't need. Free, local, no API required.

Usage:
    from promptcruncher import crunch

    result = crunch("Could you please help me understand what a binary tree is?")
    print(result.text)       # compressed prompt
    print(result.stats)      # token savings
"""

from .compressor import Compressor
from .tokens import compression_stats


class CrunchResult:
    def __init__(self, original: str, compressed: str, stats: dict):
        self.original = original
        self.text = compressed
        self.stats = stats

    def __str__(self):
        return self.text

    def __repr__(self):
        return (
            f"CrunchResult("
            f"tokens={self.stats['original_tokens']}→{self.stats['compressed_tokens']}, "
            f"saved={self.stats['compression_ratio']}%)"
        )

    def report(self):
        s = self.stats
        print(f"  Original : {s['original_tokens']} tokens")
        print(f"  Compressed: {s['compressed_tokens']} tokens")
        print(f"  Saved    : {s['tokens_saved']} tokens ({s['compression_ratio']}%)")
        if not s["tiktoken_available"]:
            print("  (token counts estimated — install tiktoken for exact counts)")


def crunch(
    text: str,
    deduplicate: bool = True,
    aggressive: bool = False,
    model: str = "gpt-4o",
) -> CrunchResult:
    """
    Compress a prompt. Returns a CrunchResult with .text and .stats.

    Args:
        text:        The prompt or context to compress.
        deduplicate: Remove repeated/near-duplicate sentences. Default True.
        aggressive:  Also strip hedging and softeners. Default False.
        model:       Model name for token counting. Default 'gpt-4o'.

    Returns:
        CrunchResult with .text (compressed) and .stats (token counts).
    """
    compressor = Compressor(deduplicate=deduplicate, aggressive=aggressive)
    compressed = compressor.compress(text)
    stats = compression_stats(text, compressed, model)
    return CrunchResult(original=text, compressed=compressed, stats=stats)
