import re
import math
import sqlite3
import threading
from collections import Counter
from datetime import datetime
from pathlib import Path

import tldextract
import whois

KNOWN_BRANDS = [
    "paypal", "google", "apple", "amazon", "microsoft",
    "facebook", "netflix", "instagram", "chase", "wellsfargo",
    "bankofamerica", "dropbox", "linkedin", "twitter",
]

SUSPICIOUS_TLDS = {"tk", "ml", "ga", "cf", "gq", "xyz", "top", "click", "loan", "work"}

_DB_PATH = Path(__file__).parent / "data" / "whois_cache.db"
_lock = threading.Lock()


def _init_db():
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS whois_cache "
            "(domain TEXT PRIMARY KEY, age_days INTEGER, fetched_at TEXT)"
        )


def _cached_domain_age(domain: str) -> int:
    """Returns domain age in days from cache or live WHOIS. Returns -1 on failure."""
    _init_db()
    with _lock:
        with sqlite3.connect(_DB_PATH) as conn:
            row = conn.execute(
                "SELECT age_days FROM whois_cache WHERE domain = ?", (domain,)
            ).fetchone()
            if row is not None:
                return row[0]

    age = _live_domain_age(domain)

    with _lock:
        with sqlite3.connect(_DB_PATH) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO whois_cache VALUES (?, ?, ?)",
                (domain, age, datetime.now().isoformat()),
            )
    return age


def _live_domain_age(domain: str) -> int:
    try:
        w = whois.whois(domain)
        created = w.creation_date
        if isinstance(created, list):
            created = created[0]
        if created:
            return (datetime.now() - created).days
    except Exception:
        pass
    return -1


def entropy(s: str) -> float:
    if not s:
        return 0.0
    p = Counter(s)
    return -sum((c / len(s)) * math.log2(c / len(s)) for c in p.values())


def check_brand_spoof(domain: str) -> int:
    d = domain.lower()
    for brand in KNOWN_BRANDS:
        if brand in d and d != brand:
            return 1
    return 0


def extract_features(url: str, fast_mode: bool = False) -> dict:
    ext = tldextract.extract(url)
    domain = ext.domain + "." + ext.suffix
    path = url.split(domain, 1)[-1] if domain in url else ""
    # Strip query string from path for depth calculation
    path_only = path.split("?")[0].split("#")[0]
    path_depth = len([s for s in path_only.split("/") if s])

    if fast_mode:
        age = -1
    else:
        age = _cached_domain_age(domain)

    # Compute noisy features on domain only — query strings skew these badly
    domain_part = ext.subdomain + "." + ext.domain if ext.subdomain else ext.domain

    return {
        # Domain-scoped features (query strings would pollute these)
        "entropy": round(entropy(domain_part), 4),
        "num_digits": sum(c.isdigit() for c in domain_part),
        "num_hyphens": domain_part.count("-"),
        "num_dots": url.count("."),
        "num_at": url.count("@"),
        "has_https": int(url.startswith("https")),
        "has_ip_address": int(bool(re.match(r"https?://\d+\.\d+\.\d+\.\d+", url))),
        "subdomain_count": ext.subdomain.count(".") + 1 if ext.subdomain else 0,
        "brand_spoof": check_brand_spoof(ext.domain),
        "domain_age_days": age,
        "tld_suspicious": int(ext.suffix in SUSPICIOUS_TLDS),
        # Engineered to avoid training-data length bias:
        # only flags URLs with tokens/base64 junk (> 75 chars is unusual for real pages)
        "url_is_long": int(len(url) > 75),
        # Registered name length (excludes TLD) — catches garbled phishing domains
        "registered_domain_length": len(ext.domain),
        # Path depth (segments) — more neutral than raw path_length
        "path_depth": path_depth,
        # Query string present — common on legitimate sites
        "has_query": int("?" in url),
    }
