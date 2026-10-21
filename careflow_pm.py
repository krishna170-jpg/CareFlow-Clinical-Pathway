"""CareFlow process-mining helpers.

Pure pandas, no Streamlit imports, so everything here can be unit-tested and
reused outside the dashboard. app.py wraps these in st.cache_data.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional

import pandas as pd

# --------------------------------------------------------------------------
# Column-role detection
# --------------------------------------------------------------------------
# Order matters: hints are tried in priority order, and a column can only be
# claimed by one role. Time is resolved first so that "Event Time" is never
# mistaken for the activity column.
ROLE_ORDER = ["time", "case", "activity", "dept", "status", "staff"]
ROLE_HINTS = {
    "time": ["timestamp", "datetime", "date time", "event time", "time", "date"],
    "case": ["case id", "patient id", "encounter", "visit id", "case"],
    "activity": ["activity", "event", "procedure", "step", "action"],
    "dept": ["department", "dept", "unit", "ward", "service line"],
    "status": ["status", "outcome", "state"],
    "staff": ["resource", "staff", "clinician", "doctor", "nurse", "assignee", "user"],
}


def _norm(x) -> str:
    return str(x).strip().lower().replace("_", " ").replace("-", " ")


def find_col(df: pd.DataFrame, hints: Iterable[str], exclude: Iterable = ()) -> Optional[str]:
    """First column whose name contains a hint. Earlier hints win over earlier columns."""
    skip = set(exclude)
    names = {c: _norm(c) for c in df.columns if c not in skip}
    for hint in hints:
        h = _norm(hint)
        for col, name in names.items():
            if h in name:
                return col
    return None


def detect_roles(df: pd.DataFrame) -> dict:
    roles, used = {}, []
    for role in ROLE_ORDER:
        col = find_col(df, ROLE_HINTS[role], exclude=used)
        roles[role] = col
        if col is not None:
            used.append(col)
    return roles


# --------------------------------------------------------------------------
# Preparation
# --------------------------------------------------------------------------
def parse_timestamps(s: pd.Series) -> pd.Series:
    """Parse to naive datetimes. Falls back to mixed-format parsing when the
    first attempt turns most values into NaT. Numeric columns are not
    reinterpreted as epoch values (they come back as NaT)."""
    if pd.api.types.is_numeric_dtype(s):
        return pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")

    def _parse(**kw):
        return pd.to_datetime(s, errors="coerce", utc=True, **kw).dt.tz_localize(None)

    out = _parse()
    if s.notna().any() and out.notna().sum() < 0.9 * s.notna().sum():
        alt = _parse(format="mixed")
        if alt.notna().sum() > out.notna().sum():
            out = alt
    return out


DEMO_DEPARTMENTS = ["Emergency", "Cardiology", "Respiratory", "Neurology", "Orthopedics", "General Medicine"]


def add_demo_department(df: pd.DataFrame, key_col) -> pd.DataFrame:
    """Reproducible SYNTHETIC department labels (same algorithm as v1)."""
    out = df.copy()
    keys = out[key_col].fillna("Unknown").astype(str)
    out["demo_department"] = keys.map(
        lambda x: DEMO_DEPARTMENTS[sum((i + 1) * ord(ch) for i, ch in enumerate(x)) % len(DEMO_DEPARTMENTS)]
    )
    return out


# --------------------------------------------------------------------------
# Filtering
# --------------------------------------------------------------------------
def apply_filters(
    df: pd.DataFrame,
    *,
    case=None,
    act=None,
    time=None,
    dept=None,
    depts: Iterable[str] = (),
    acts: Iterable[str] = (),
    date_range=None,
    keep_whole_cases: bool = True,
) -> pd.DataFrame:
    """Empty selections mean 'no restriction'.

    keep_whole_cases: when filtering by activity, keep every event of any case
    that contains a selected activity, so pathways are not cut into fragments.
    date_range: (start, end) dates; ignored when it spans the full data range,
    so rows with missing timestamps are not dropped needlessly."""
    mask = pd.Series(True, index=df.index)
    depts, acts = list(depts), list(acts)

    if dept and depts:
        mask &= df[dept].astype(str).isin(depts)

    if act and acts:
        hit = df[act].fillna("Unknown activity").astype(str).isin(acts)
        if keep_whole_cases and case:
            mask &= df[case].isin(df.loc[hit, case].dropna().unique())
        else:
            mask &= hit

    if time and date_range and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        valid = df[time].dropna()
        full = (not valid.empty) and valid.min().normalize() >= start and valid.max().normalize() <= end
        if not full:
            mask &= (df[time] >= start) & (df[time] < end + pd.Timedelta(days=1))

    return df[mask]


# --------------------------------------------------------------------------
# Mining
# --------------------------------------------------------------------------
def _ordered(df, case, act, time=None) -> pd.DataFrame:
    cols = [case, act] + ([time] if time else [])
    w = df[cols].copy()
    w[act] = w[act].fillna("Unknown activity").astype(str)
    if time:
        w = w.sort_values(time, kind="stable", na_position="last")
    return w


def mine_transitions(df, case, act, time=None) -> pd.DataFrame:
    """Directly-follows relations with frequency and (if timestamps) wait times in hours."""
    w = _ordered(df, case, act, time)
    g = w.groupby(case, sort=False)
    w["To activity"] = g[act].shift(-1)
    if time:
        w["_wait"] = (g[time].shift(-1) - w[time]).dt.total_seconds() / 3600
    t = w.dropna(subset=["To activity"]).rename(columns={act: "From activity"})
    if t.empty:
        cols = ["From activity", "To activity", "Transitions"]
        return pd.DataFrame(columns=cols + (["Avg wait (h)", "Median wait (h)"] if time else []))
    gb = t.groupby(["From activity", "To activity"])
    out = gb.size().rename("Transitions").to_frame()
    if time:
        out["Avg wait (h)"] = gb["_wait"].mean().round(2)
        out["Median wait (h)"] = gb["_wait"].median().round(2)
    return out.reset_index().sort_values("Transitions", ascending=False, ignore_index=True)


def _finish_variants(v: pd.DataFrame) -> pd.DataFrame:
    v = v.sort_values("Cases", ascending=False, ignore_index=True)
    v.insert(0, "Variant", [f"V{i}" for i in range(1, len(v) + 1)])
    total = v["Cases"].sum()
    v["Share of cases (%)"] = (v["Cases"] / total * 100).round(1) if total else 0.0
    v["Steps"] = v["Observed pathway"].str.count("→") + 1
    return v


def mine_variants(df, case, act, time=None):
    """Returns (variants table, Series mapping case -> pathway string)."""
    w = _ordered(df, case, act, time)
    seq = w.groupby(case, sort=False)[act].agg(" → ".join).rename("Observed pathway")
    v = seq.value_counts().rename_axis("Observed pathway").reset_index(name="Cases")
    return _finish_variants(v), seq


def case_durations(df, case, time) -> pd.DataFrame:
    """First-to-last recorded event per case. Not necessarily length of stay."""
    t = df.dropna(subset=[time]).groupby(case)[time].agg(Start="min", End="max", Events="size")
    t["Elapsed hours"] = (t["End"] - t["Start"]).dt.total_seconds() / 3600
    return t.reset_index()


# --------------------------------------------------------------------------
# Normalising externally produced process-mining outputs (CSV)
# --------------------------------------------------------------------------
_TOKEN = re.compile(r"[^a-z0-9]+")


def _tokens(col) -> set:
    return set(_TOKEN.split(str(col).lower()))


def _pick(df, hints, numeric=None):
    for h in hints:
        for c in df.columns:
            if h in _tokens(c):
                is_num = pd.api.types.is_numeric_dtype(df[c])
                if numeric is None or numeric == is_num:
                    return c
    return None


def normalize_transitions(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Map a precomputed directly-follows table to the standard columns, or None."""
    src = _pick(df, ["from", "source", "src", "predecessor", "prev", "previous"], numeric=False)
    dst = _pick(df, ["to", "target", "dst", "successor", "next"], numeric=False)
    if src is None or dst is None or src == dst:
        return None
    cnt = _pick(df, ["transitions", "count", "frequency", "freq", "cases", "n"], numeric=True)
    out = pd.DataFrame({"From activity": df[src].astype(str), "To activity": df[dst].astype(str)})
    out["Transitions"] = pd.to_numeric(df[cnt], errors="coerce").fillna(0) if cnt else 1
    # Only trust a wait column whose name states the unit is hours.
    for c in df.columns:
        t = _tokens(c)
        if (
            t & {"wait", "waiting", "avg", "mean", "average", "duration"}
            and t & {"h", "hr", "hrs", "hour", "hours"}
            and pd.api.types.is_numeric_dtype(df[c])
        ):
            out["Avg wait (h)"] = pd.to_numeric(df[c], errors="coerce")
            break
    agg = {"Transitions": "sum"}
    if "Avg wait (h)" in out:
        agg["Avg wait (h)"] = "mean"
    return out.groupby(["From activity", "To activity"], as_index=False).agg(agg).sort_values(
        "Transitions", ascending=False, ignore_index=True
    )


def normalize_variants(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Map a precomputed variants table to the standard columns, or None."""
    cands = [
        c for c in df.columns
        if _tokens(c) & {"variant", "pathway", "path", "sequence", "trace"} and not pd.api.types.is_numeric_dtype(df[c])
    ]
    if not cands:
        return None
    path = max(cands, key=lambda c: df[c].astype(str).str.len().mean())
    cnt = _pick(df, ["cases", "count", "frequency", "freq", "n"], numeric=True)
    out = pd.DataFrame({"Observed pathway": df[path].astype(str)})
    out["Cases"] = pd.to_numeric(df[cnt], errors="coerce").fillna(0).astype(int) if cnt else 1
    out["Observed pathway"] = out["Observed pathway"].str.replace(r"\s*(?:->|>|;|\|)\s*", " → ", regex=True)
    out = out.groupby("Observed pathway", as_index=False)["Cases"].sum()
    return _finish_variants(out)
