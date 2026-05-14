import pickle
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Phishing Detector", page_icon="🛡️", layout="centered")

MODEL_PATH = Path(__file__).parent / "model.pkl"


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        return None
    return pickle.load(open(MODEL_PATH, "rb"))


model = load_model()

st.title("🛡️ Phishing URL Analyzer")
st.caption("ML risk scoring · SHAP explainability · VirusTotal intelligence")

if model is None:
    st.error(
        "**model.pkl not found.** Run `python train.py` first to train the model, "
        "then reload this page."
    )
    st.sidebar.empty()
    raise SystemExit(0)

fast_mode = st.sidebar.toggle("Fast mode (skip WHOIS lookup)", value=True)
run_vt = st.sidebar.toggle("VirusTotal check", value=True)

url = st.text_input("Enter a URL to analyze", placeholder="https://example.com")

if not url:
    st.stop()

# Normalize: add https:// if no protocol given (e.g. user types "google.com")
if not url.startswith(("http://", "https://")):
    url = "https://" + url

# --- Feature extraction ---
from features import extract_features  # noqa: E402 (import after model check)

with st.spinner("Extracting features..."):
    try:
        features = extract_features(url, fast_mode=fast_mode)
    except Exception as e:
        st.error(f"Feature extraction failed: {e}")
        st.stop()

X = pd.DataFrame([features]).fillna(-1)
score = model.predict_proba(X)[0][1]

# --- Risk score ---
if score > 0.7:
    color, verdict, delta_color = "🔴", "High risk", "inverse"
elif score > 0.4:
    color, verdict, delta_color = "🟡", "Medium risk", "off"
else:
    color, verdict, delta_color = "🟢", "Low risk", "normal"

st.metric(
    label=f"{color} Phishing risk score",
    value=f"{score:.0%}",
    delta=verdict,
    delta_color=delta_color,
)
st.progress(float(score))

# --- Extracted signals ---
with st.expander("🔍 Extracted signals", expanded=True):
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, (k, v) in enumerate(features.items()):
        display = round(v, 4) if isinstance(v, float) else v
        cols[i % 3].metric(k.replace("_", " "), display)

# --- SHAP explainability ---
_FEATURE_LABELS = {
    "entropy":                  "Domain randomness",
    "num_digits":               "Digits in domain",
    "num_hyphens":              "Hyphens in domain",
    "num_dots":                 "Dots in URL",
    "num_at":                   "@ symbols",
    "has_https":                "Uses HTTPS",
    "has_ip_address":           "IP address as host",
    "subdomain_count":          "Subdomain depth",
    "brand_spoof":              "Brand name in domain",
    "domain_age_days":          "Domain age (days)",
    "tld_suspicious":           "Suspicious top-level domain",
    "url_is_long":              "Unusually long URL",
    "registered_domain_length": "Domain name length",
    "path_depth":               "URL path depth",
    "has_query":                "Has query string (?...)",
}

with st.expander("🧠 What influenced this score?", expanded=True):
    try:
        from explain import explain  # noqa: E402

        shap_vals = explain(features)
        st.caption("Each row shows one signal the model noticed and whether it pushed the score toward phishing or safety.")

        for feat, impact in list(shap_vals.items())[:8]:
            label = _FEATURE_LABELS.get(feat, feat.replace("_", " ").title())
            val = features.get(feat, "?")
            if impact > 0.1:
                icon, note = "🔴", "pushed toward **phishing**"
            elif impact < -0.1:
                icon, note = "🟢", "pushed toward **safe**"
            else:
                icon, note = "⚪", "little effect"
            st.markdown(f"{icon} **{label}** = `{val}` — {note}")
    except Exception as e:
        st.warning(f"SHAP explanation unavailable: {e}")

# --- VirusTotal ---
if run_vt:
    with st.expander("🦠 VirusTotal intelligence", expanded=True):
        with st.spinner("Checking VirusTotal (this takes ~5s)..."):
            from virustotal import virustotal_check  # noqa: E402

            vt = virustotal_check(url)

        if "error" in vt:
            st.warning(vt["error"])
        else:
            stats = vt["stats"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🚨 Malicious", stats.get("malicious", 0))
            c2.metric("⚠️ Suspicious", stats.get("suspicious", 0))
            c3.metric("✅ Harmless", stats.get("harmless", 0))
            c4.metric("❓ Undetected", stats.get("undetected", 0))

            engines = vt.get("engines", {})
            if engines:
                st.markdown("**Engines that flagged this URL:**")
                _VERDICT_COLORS = {
                    "malicious": "🔴",
                    "phishing":  "🔴",
                    "suspicious":"🟡",
                    "spam":      "🟡",
                    "harmless":  "🟢",
                    "clean":     "🟢",
                }
                for engine, verdict in sorted(engines.items()):
                    icon = next((v for k, v in _VERDICT_COLORS.items() if k in verdict.lower()), "⚪")
                    st.markdown(f"{icon} **{engine}** — {verdict}")
            else:
                st.success("No engines flagged this URL.")
