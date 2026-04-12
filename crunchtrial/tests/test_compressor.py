"""
Tests for promptcruncher.
Run with: python -m pytest tests/ -v
"""

import pytest
from promptcruncher import crunch


# ── Pleasantries ─────────────────────────────────────────────────────────────

def test_strips_sure():
    result = crunch("Sure! Here is how binary trees work.")
    assert "sure" not in result.text.lower()
    assert "binary trees" in result.text.lower()

def test_strips_happy_to_help():
    result = crunch("Happy to help! A linked list is a data structure.")
    assert "happy to help" not in result.text.lower()
    assert "linked list" in result.text.lower()

def test_strips_certainly():
    result = crunch("Certainly! Let me explain recursion.")
    assert "certainly" not in result.text.lower()
    assert "recursion" in result.text.lower()

def test_strips_great_question():
    result = crunch("Great question! The answer is 42.")
    assert "great question" not in result.text.lower()
    assert "42" in result.text


# ── Filler patterns ───────────────────────────────────────────────────────────

def test_strips_in_order_to():
    result = crunch("In order to fix this bug, restart the server.")
    assert "in order to" not in result.text.lower()
    assert "fix this bug" in result.text.lower()

def test_strips_it_is_important_to_note():
    result = crunch("It is important to note that Python is dynamically typed.")
    assert "important to note" not in result.text.lower()
    assert "python" in result.text.lower()

def test_strips_basically():
    result = crunch("Basically, you need to call the API with your key.")
    assert "basically" not in result.text.lower()
    assert "api" in result.text.lower()


# ── Deduplication ─────────────────────────────────────────────────────────────

def test_deduplicates_repeated_sentences():
    text = (
        "Python is a dynamically typed language. "
        "Python is a dynamically typed language. "
        "Use it for scripting."
    )
    result = crunch(text)
    # Should appear only once
    lower = result.text.lower()
    first = lower.find("dynamically typed")
    second = lower.find("dynamically typed", first + 1)
    assert second == -1, "Duplicate sentence was not removed"

def test_dedup_off():
    text = "Python is great. Python is great."
    result = crunch(text, deduplicate=False)
    assert result.text.lower().count("python is great") == 2


# ── Preservation ──────────────────────────────────────────────────────────────

def test_preserves_code_content():
    text = "Please run: `pip install requests` to install the library."
    result = crunch(text)
    assert "pip install requests" in result.text

def test_preserves_numbers():
    text = "The API rate limit is 1000 requests per minute."
    result = crunch(text)
    assert "1000" in result.text

def test_preserves_urls():
    text = "See the docs at https://docs.example.com/api for details."
    result = crunch(text)
    assert "https://docs.example.com/api" in result.text

def test_preserves_error_messages():
    text = "You got: TypeError: 'NoneType' object is not subscriptable"
    result = crunch(text)
    assert "NoneType" in result.text


# ── Stats ────────────────────────────────────────────────────────────────────

def test_stats_returned():
    result = crunch("Sure! Happy to help. Here is your answer.")
    assert "original_tokens" in result.stats
    assert "compressed_tokens" in result.stats
    assert "tokens_saved" in result.stats
    assert "compression_ratio" in result.stats

def test_compression_reduces_tokens():
    verbose = (
        "Sure! Great question! I'd be happy to help you with that. "
        "It is important to note that, in order to understand recursion, "
        "you basically need to understand recursion. "
        "I hope this helps! Let me know if you have any other questions!"
    )
    result = crunch(verbose)
    assert result.stats["tokens_saved"] > 0

def test_already_terse_prompt_unchanged():
    terse = "Fix the null pointer in auth.py line 42."
    result = crunch(terse)
    # Should be essentially the same, maybe minor whitespace changes
    assert result.stats["tokens_saved"] <= 2


# ── Aggressive mode ───────────────────────────────────────────────────────────

def test_aggressive_strips_hedging():
    text = "I was wondering if you could perhaps help me with this."
    result = crunch(text, aggressive=True)
    assert "wondering" not in result.text.lower()

def test_aggressive_more_savings_than_normal():
    text = (
        "I was wondering if you could help me understand, if that's okay, "
        "how to implement a binary search tree. If possible, please include examples."
    )
    normal = crunch(text, aggressive=False)
    aggressive = crunch(text, aggressive=True)
    assert aggressive.stats["tokens_saved"] >= normal.stats["tokens_saved"]
