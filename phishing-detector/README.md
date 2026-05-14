# Phishing URL Analyzer

ML-based phishing detection with SHAP explainability and VirusTotal integration.

## Setup

```bash
pip install -r requirements.txt
```

## Datasets

Download both into `data/`:

| File | Source |
|---|---|
| `data/openphish_feed.txt` | https://openphish.com/feed.txt — plain text, one URL per line |
| `data/tranco.csv` | https://tranco-list.eu/ — format: `rank,domain` (no header) |

## Train

```bash
cd phishing-detector
python train.py
```

This produces `model.pkl`. Training uses `fast_mode=True` (no WHOIS) — takes ~2 min.

## Configure VirusTotal

Edit `.env`:

```
VT_API_KEY=your_key_here
```

Get a free key at https://www.virustotal.com/gui/join-us (500 req/day).

## Run

```bash
streamlit run app.py
```

## Sidebar options

- **Fast mode** — skips WHOIS lookup (instant, trades `domain_age_days` accuracy for speed)
- **VirusTotal check** — toggle off to skip the ~5s VT API call

## Features extracted

| Feature | Description |
|---|---|
| `url_length` | Total URL character count |
| `domain_length` | Domain + TLD length |
| `entropy` | Shannon entropy of the URL |
| `num_digits` | Count of digit characters |
| `num_hyphens` | Hyphens in URL |
| `num_dots` | Dots in URL |
| `num_at` | `@` symbols (redirect trick) |
| `num_slashes` | Slash count |
| `has_https` | 1 if HTTPS |
| `has_ip_address` | 1 if host is a raw IP |
| `subdomain_count` | Number of subdomain levels |
| `path_length` | Length of URL path |
| `brand_spoof` | 1 if domain contains a known brand name |
| `domain_age_days` | Days since domain registered (WHOIS) |
| `tld_suspicious` | 1 if TLD is in high-abuse list |
