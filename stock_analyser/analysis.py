"""
Pure computation backend — no plotting, no side effects.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

TRADING_DAYS = 252
BENCHMARK    = "SPY"


# ── Data ──────────────────────────────────────────────────────────────────────

def fetch_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    all_tickers = list(dict.fromkeys(tickers + [BENCHMARK]))
    raw = yf.download(all_tickers, start=start, end=end, progress=False, auto_adjust=True)
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
    prices = prices.dropna(how="all")
    missing = [t for t in all_tickers if t not in prices.columns]
    if missing:
        raise ValueError(f"Could not fetch data for: {missing}")
    return prices


# ── Returns ───────────────────────────────────────────────────────────────────

def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def portfolio_returns(returns: pd.DataFrame, tickers: list[str], weights: list[float]) -> pd.Series:
    w = np.array(weights, dtype=float)
    w /= w.sum()
    return returns[tickers].dot(w).rename("Portfolio")


def cumulative_returns(returns: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return (1 + returns).cumprod() - 1


# ── Risk ──────────────────────────────────────────────────────────────────────

def annualised_return(returns: pd.Series) -> float:
    n_years = len(returns) / TRADING_DAYS
    return (1 + returns).prod() ** (1 / n_years) - 1


def annualised_volatility(returns: pd.Series) -> float:
    return returns.std() * np.sqrt(TRADING_DAYS)


def sharpe_ratio(returns: pd.Series, risk_free: float) -> float:
    excess = annualised_return(returns) - risk_free
    vol = annualised_volatility(returns)
    return excess / vol if vol != 0 else np.nan


def max_drawdown(returns: pd.Series) -> float:
    cum = (1 + returns).cumprod()
    dd  = (cum - cum.cummax()) / cum.cummax()
    return dd.min()


def value_at_risk(returns: pd.Series, confidence: float = 0.95) -> float:
    return norm.ppf(1 - confidence, returns.mean(), returns.std())


def beta(port_returns: pd.Series, bench_returns: pd.Series) -> float:
    cov = np.cov(port_returns, bench_returns)
    return cov[0, 1] / cov[1, 1]


# ── Top-level entry point ─────────────────────────────────────────────────────

def run_analysis(
    tickers: list[str],
    weights: list[float],
    start:   str,
    end:     str,
    risk_free: float = 0.0525,
) -> dict:
    """
    Returns a dict of everything the UI needs:
      prices, returns, port_ret, bench_ret, metrics, cum_returns, drawdown_series
    """
    prices  = fetch_prices(tickers, start, end)
    returns = daily_returns(prices)

    port_ret  = portfolio_returns(returns, tickers, weights)
    bench_ret = returns[BENCHMARK]

    cum = cumulative_returns(
        pd.concat([port_ret, bench_ret] + [returns[t] for t in tickers], axis=1)
    ) * 100

    cum_port  = (1 + port_ret).cumprod()
    dd_series = (cum_port - cum_port.cummax()) / cum_port.cummax() * 100

    metrics = {
        "Annualised Return":     annualised_return(port_ret),
        "Annualised Volatility": annualised_volatility(port_ret),
        "Sharpe Ratio":          sharpe_ratio(port_ret, risk_free),
        "Max Drawdown":          max_drawdown(port_ret),
        "VaR (95%, 1-day)":     value_at_risk(port_ret),
        "Beta (vs SPY)":         beta(port_ret, bench_ret),
    }

    stock_metrics = {}
    for t in tickers:
        stock_metrics[t] = {
            "Annualised Return":     annualised_return(returns[t]),
            "Annualised Volatility": annualised_volatility(returns[t]),
            "Sharpe Ratio":          sharpe_ratio(returns[t], risk_free),
            "Max Drawdown":          max_drawdown(returns[t]),
        }

    return {
        "prices":        prices,
        "returns":       returns,
        "port_ret":      port_ret,
        "bench_ret":     bench_ret,
        "cum_returns":   cum,
        "dd_series":     dd_series,
        "metrics":       metrics,
        "stock_metrics": stock_metrics,
        "tickers":       tickers,
        "weights":       weights,
    }
