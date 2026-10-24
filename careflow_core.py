"""Streamlit-free logic for CareFlow, covered by tests/test_core.py.

Everything here is calculated from the event log you pass in; nothing is hard-coded or invented.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

STAGE_COLORS = {
    "admission": "#0D9488",     # registration / admission
    "diagnostics": "#2563EB",   # assessment / diagnostics
    "treatment": "#7C6FE0",     # treatment / procedure
    "completed": "#16A34A",     # discharge / completed
    "transfer": "#38BDF8",      # transfer / departure
    "waiting": "#D97706",       # waiting / delay
    "attention": "#DC2626",     # exception / attention required
    "other": "#64748B",         # unclassified activity
}
STAGE_META = [("admission", "Admission", "🏥"), ("waiting", "Waiting / delay", "⏳"), ("diagnostics", "Assessment", "🩺"),
              ("treatment", "Treatment", "💉"), ("transfer", "Transfer / departure", "🚑"),
              ("completed", "Discharge / completed", "✅"), ("attention", "Exceptions", "⚠️"), ("other", "Other activity", "📋")]
STAGE_LABELS = {k: label for k, label, _ in STAGE_META}
# Order matters: the first matching rule wins.
STAGE_RULES = [
    ("completed", ("discharg", "complete", "completed", "depart", "end of care", "follow-up complete")),
    ("waiting", ("wait", "pending", "queue", "hold", "delay", "await")),
    ("attention", ("exception", "error", "cancel", "cancell", "rework", "escalat", "failed", "failure")),
    ("transfer", ("transfer", "left ed", "left the", "transport", "moved to", "referral")),
    ("diagnostics", ("diagnos", "test", "lab", "laboratory", "scan", "imaging", "assessment", "investigat", "triage", "exam")),
    ("treatment", ("treat", "medicat", "therapy", "procedure", "surgery", "operation", "intervention", "prescri")),
    ("admission", ("admi", "register", "registr", "arrival", "intake", "check-in", "check in", "enrol", "enroll")),
]


def classify_stage(activity, overrides=None) -> str:
    """Stage key for an activity label. A user override always wins over the keyword rules."""
    label = str(activity)
    if overrides and label in overrides and overrides[label] in STAGE_COLORS:
        return overrides[label]
    low = label.strip().lower()
    for stage, words in STAGE_RULES:
        if any(w in low for w in words):
            return stage
    return "other"


def fmt_dwell(h) -> str:
    if h is None or pd.isna(h):
        return "n/a"
    return f"{h * 60:,.0f} min" if h < 1 else (f"{h:,.1f} hrs" if h < 48 else f"{h / 24:,.1f} days")


def stage_summary(df, case, act, time=None, overrides=None, targets=None) -> pd.DataFrame:
    """Per stage: cases, events, average time until the next event in the same case, share of visits over target."""
    if df is None or df.empty or not case or not act:
        return pd.DataFrame()
    d = df[[case, act] + ([time] if time else [])].copy()
    d[act] = d[act].fillna("Unknown activity").astype(str)
    lookup = {a: classify_stage(a, overrides) for a in d[act].unique()}
    d["_stage"] = d[act].map(lookup)
    d["_h"] = np.nan
    if time:
        d[time] = pd.to_datetime(d[time], errors="coerce")
        d = d.sort_values([case, time], kind="stable")
        d["_h"] = (d.groupby(case)[time].shift(-1) - d[time]).dt.total_seconds() / 3600
        d.loc[d["_h"] < 0, "_h"] = np.nan
    g = d.groupby("_stage").agg(cases=(case, "nunique"), events=(act, "size"), avg_h=("_h", "mean"),
                                names=(act, lambda x: ", ".join(x.value_counts().index[:2])))
    g["over_pct"] = np.nan
    for stage, target in (targets or {}).items():
        if stage in g.index and target and target > 0:
            h = d.loc[d["_stage"] == stage, "_h"].dropna()
            if len(h):
                g.loc[stage, "over_pct"] = float((h > target).mean() * 100)
    return g


def week_over_week(df, case, time):
    """New cases in the latest 7 days of the log versus the 7 days before. None if it cannot be computed."""
    if df is None or df.empty or not case or not time:
        return None
    t = pd.to_datetime(df[time], errors="coerce")
    starts = pd.Series(t.values, index=df[case].values).dropna().groupby(level=0).min()
    if starts.empty:
        return None
    end = starts.max()
    cur = int((starts > end - pd.Timedelta(days=7)).sum())
    prev = int(((starts > end - pd.Timedelta(days=14)) & (starts <= end - pd.Timedelta(days=7))).sum())
    if prev == 0 or (starts.min() > end - pd.Timedelta(days=14)):
        return None
    return {"cur": cur, "prev": prev, "pct": (cur - prev) / prev * 100}


def completeness(df) -> pd.Series:
    """Percent of non-empty values per field, lowest first."""
    return (df.notna().mean() * 100).sort_values() if df is not None and not df.empty else pd.Series(dtype=float)


def arrival_forecast(starts, horizon_days: int = 7):
    """Seasonal-average forecast of arrivals per hour (same weekday and hour in the past).

    Returns (forecast DataFrame[Time, Expected arrivals], backtest dict or None).
    The backtest holds out the last 7 days and compares the model's MAE with 'same hour last week'.
    """
    s = pd.to_datetime(pd.Series(starts), errors="coerce").dropna()
    if len(s) < 50:
        return pd.DataFrame(), None
    hourly = s.dt.floor("h").value_counts().sort_index()
    idx = pd.date_range(hourly.index.min(), hourly.index.max(), freq="h")
    hourly = hourly.reindex(idx, fill_value=0)

    def profile(series):
        return series.groupby([series.index.dayofweek, series.index.hour]).mean()

    prof = profile(hourly)
    future = pd.date_range(hourly.index.max() + pd.Timedelta(hours=1), periods=horizon_days * 24, freq="h")
    exp = [float(prof.get((t.dayofweek, t.hour), np.nan)) for t in future]
    forecast = pd.DataFrame({"Time": future, "Expected arrivals": exp})

    backtest = None
    if len(hourly) >= 24 * 21:
        test, train = hourly.iloc[-168:], hourly.iloc[:-168]
        p = profile(train)
        pred = np.array([p.get((t.dayofweek, t.hour), np.nan) for t in test.index])
        naive = hourly.shift(168).iloc[-168:].values
        ok = ~np.isnan(pred) & ~np.isnan(naive)
        if ok.any():
            backtest = {"mae_model": float(np.mean(np.abs(pred[ok] - test.values[ok]))),
                        "mae_naive": float(np.mean(np.abs(naive[ok] - test.values[ok]))), "hours": int(ok.sum())}
    return forecast, backtest
