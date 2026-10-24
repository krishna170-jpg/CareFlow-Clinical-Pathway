import numpy as np
import pandas as pd
import pytest

import careflow_core as core


def test_classify_default_rules():
    assert core.classify_stage("Registration") == "admission"
    assert core.classify_stage("Ambulance Arrival") == "admission"
    assert core.classify_stage("Triage") == "diagnostics"
    assert core.classify_stage("Left ED") == "transfer"
    assert core.classify_stage("Waiting for bed") == "waiting"
    assert core.classify_stage("Discharge") == "completed"
    assert core.classify_stage("Something else") == "other"


def test_override_wins():
    assert core.classify_stage("Left ED", {"Left ED": "completed"}) == "completed"
    assert core.classify_stage("Left ED", {"Left ED": "not-a-stage"}) == "transfer"


@pytest.mark.parametrize("h,expected", [(None, "n/a"), (float("nan"), "n/a"), (0.5, "30 min"), (2.0, "2.0 hrs"), (72, "3.0 days")])
def test_fmt_dwell(h, expected):
    assert core.fmt_dwell(h) == expected


def _log():
    return pd.DataFrame({
        "id": [1, 1, 1, 2, 2, 2],
        "act": ["Registration", "Triage", "Discharge"] * 2,
        "t": pd.to_datetime(["2026-01-01 08:00", "2026-01-01 09:00", "2026-01-01 13:00",
                             "2026-01-02 08:00", "2026-01-02 08:30", "2026-01-02 14:00"]),
    })


def test_stage_summary_average_and_targets():
    g = core.stage_summary(_log(), "id", "act", "t", targets={"diagnostics": 3})
    assert g.loc["admission", "avg_h"] == pytest.approx((1 + 0.5) / 2)
    assert g.loc["diagnostics", "avg_h"] == pytest.approx((4 + 5.5) / 2)
    assert g.loc["diagnostics", "over_pct"] == pytest.approx(100.0)
    assert np.isnan(g.loc["admission", "over_pct"])
    assert g.loc["completed", "cases"] == 2


def test_stage_summary_override_moves_activity():
    g = core.stage_summary(_log(), "id", "act", "t", overrides={"Triage": "treatment"})
    assert "treatment" in g.index and "diagnostics" not in g.index


def test_stage_summary_empty():
    assert core.stage_summary(pd.DataFrame(), "id", "act", "t").empty


def test_week_over_week():
    days = pd.date_range("2026-01-01", periods=21, freq="D")
    rows = [{"id": f"p{i}", "t": d} for i, d in enumerate(days) for _ in range(1)]
    rows += [{"id": f"q{i}", "t": days[-1] - pd.Timedelta(hours=i)} for i in range(5)]  # extra recent arrivals
    r = core.week_over_week(pd.DataFrame(rows), "id", "t")
    assert r["cur"] > r["prev"] and r["pct"] > 0


def test_week_over_week_needs_two_weeks():
    assert core.week_over_week(_log(), "id", "t") is None


def test_completeness_orders_lowest_first():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [1, None, None, 4]})
    assert list(core.completeness(df).index) == ["b", "a"]


def test_arrival_forecast_shape_and_backtest():
    rng = np.random.RandomState(0)
    start = pd.Timestamp("2026-01-01")
    times = [start + pd.Timedelta(hours=int(h)) for h in rng.randint(0, 24 * 28, 3000)]
    fc, bt = core.arrival_forecast(pd.Series(times), 7)
    assert len(fc) == 7 * 24 and fc["Expected arrivals"].notna().all()
    assert bt is not None and bt["hours"] > 100


def test_arrival_forecast_too_little_data():
    fc, bt = core.arrival_forecast(pd.Series(pd.date_range("2026-01-01", periods=10, freq="h")))
    assert fc.empty and bt is None
