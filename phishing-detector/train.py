import pickle
import random
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from features import extract_features

PHISH_FEED = "data/openphish_feed.txt"  # one URL per line, no header
LEGIT_CSV = "data/tranco.csv"  # format: rank,domain (no header)

# Representative paths covering depth 0–3 and query strings
_LEGIT_PATHS = [
    # No path
    "", "/",
    # Depth 1
    "/home", "/about", "/contact", "/login", "/signup", "/products",
    "/services", "/blog", "/news", "/help", "/support", "/account",
    "/settings", "/search", "/privacy", "/terms", "/faq", "/pricing",
    "/dashboard", "/download", "/en", "/us",
    # Depth 2
    "/en/us", "/help/support", "/account/settings", "/blog/post",
    "/gui/home", "/app/dashboard", "/user/profile", "/docs/api",
    "/news/article", "/auth/login", "/web/app", "/help/center",
    "/about/team", "/store/checkout", "/products/list",
    # Depth 3
    "/gui/home/upload", "/help/center/article", "/docs/api/reference",
    "/app/settings/profile", "/en/us/home", "/user/dashboard/overview",
    "/products/category/item", "/support/ticket/open",
    # With query strings (very common on real sites)
    "/search?q=test", "/products?page=2", "/blog?tag=news",
    "/?ref=home", "/login?redirect=%2Fdashboard",
    # Long URLs (>75 chars total with domain) to train url_is_long=0 for normal sites
    "/docs/getting-started/installation/windows",
    "/help/center/billing/subscription/manage",
]

_LEGIT_SUBDOMAINS = ["", "www.", "www.", "www.", "m.", "app.", "mail.", "shop.", "api."]


def _augment_url(domain: str, seed: int) -> str:
    rng = random.Random(seed)
    prefix = rng.choice(_LEGIT_SUBDOMAINS)
    path = rng.choice(_LEGIT_PATHS)
    return "https://" + prefix + domain + path


def load_data() -> pd.DataFrame:
    with open(PHISH_FEED) as f:
        urls = [line.strip() for line in f if line.strip()]
    phish = pd.DataFrame({"url": urls, "label": 1})

    legit_raw = pd.read_csv(LEGIT_CSV, header=None, names=["rank", "domain"])
    legit_raw = legit_raw.sample(len(phish), random_state=42).reset_index(drop=True)
    legit_raw["url"] = [
        _augment_url(domain, i)
        for i, domain in enumerate(legit_raw["domain"])
    ]
    legit = legit_raw[["url"]].copy()
    legit["label"] = 0

    df = pd.concat([phish, legit], ignore_index=True)
    print(f"Dataset: {len(phish)} phishing + {len(legit)} legitimate = {len(df)} total")
    return df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    errors = 0
    for url in df["url"]:
        try:
            # fast_mode=True skips slow WHOIS during training; set False for full features
            rows.append(extract_features(url, fast_mode=True))
        except Exception:
            rows.append({})
            errors += 1
    if errors:
        print(f"Skipped {errors} URLs due to extraction errors ({errors/len(df):.1%})")
    return pd.DataFrame(rows).fillna(-1)


if __name__ == "__main__":
    print("Loading data...")
    df = load_data()

    print("Extracting features...")
    X = build_feature_matrix(df)
    y = df["label"]

    print(f"Feature matrix: {X.shape[0]} rows, {X.shape[1]} columns")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training LightGBM...")
    model = LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=63,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)])

    print("\nEvaluation on test set:")
    print(classification_report(y_test, model.predict(X_test)))

    pickle.dump(model, open("model.pkl", "wb"))
    print("Saved model.pkl")
