#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
import pandas as pd

def main():
    p = argparse.ArgumentParser(description="CareFlow Week 3 event-log validation and process analytics")
    p.add_argument("--input", required=True)
    p.add_argument("--output-dir", default="reports/week3")
    a = p.parse_args()
    src, out = Path(a.input), Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        print(f"ERROR: input file not found: {src}", file=sys.stderr); return 2
    raw = pd.read_csv(src)
    required = {"case_id", "activity", "timestamp"}
    missing = required - set(raw.columns)
    if missing:
        print("ERROR: missing required columns: " + ", ".join(sorted(missing)), file=sys.stderr); return 2

    df = raw.copy()
    df["case_id"] = df["case_id"].astype("string").str.strip()
    df["activity"] = df["activity"].astype("string").str.strip()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    invalid = df["case_id"].isna() | (df["case_id"] == "") | df["activity"].isna() | (df["activity"] == "") | df["timestamp"].isna()
    invalid_rows = int(invalid.sum())
    checks = [
        {"check":"Required columns present","passed":True,"details":", ".join(sorted(required))},
        {"check":"Rows excluded for blank/missing case, activity, or invalid timestamp","passed":invalid_rows == 0,"details":invalid_rows},
        {"check":"Unparseable timestamps","passed":int(df["timestamp"].isna().sum()) == 0,"details":int(df["timestamp"].isna().sum())},
    ]
    df = df.loc[~invalid].copy()
    if df.empty:
        print("ERROR: no valid events remain.", file=sys.stderr); return 2
    if "sequence" in df.columns:
        df["sequence"] = pd.to_numeric(df["sequence"], errors="coerce")
    sort_cols = ["case_id", "timestamp"] + (["sequence"] if "sequence" in df.columns else [])
    df = df.sort_values(sort_cols, kind="stable").reset_index(drop=True)
    checks.extend([
        {"check":"Exact duplicate rows","passed":int(df.duplicated().sum()) == 0,"details":int(df.duplicated().sum())},
        {"check":"Duplicate (case_id, sequence) pairs","passed":int(df.duplicated(["case_id","sequence"]).sum()) == 0 if "sequence" in df.columns else None,"details":int(df.duplicated(["case_id","sequence"]).sum()) if "sequence" in df.columns else "sequence column absent"},
    ])
    pd.DataFrame(checks).to_csv(out/"data_quality_checks.csv", index=False)
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df.to_csv(out/"cleaned_event_log.csv", index=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    cases = df.groupby("case_id", sort=False).agg(event_count=("activity","size"), start_time=("timestamp","min"), end_time=("timestamp","max"), distinct_activities=("activity","nunique")).reset_index()
    cases["case_duration_minutes"] = (cases["end_time"]-cases["start_time"]).dt.total_seconds()/60
    cases.to_csv(out/"case_summary.csv", index=False)

    acts = df.groupby("activity").agg(event_count=("case_id","size"), case_count=("case_id","nunique")).reset_index().sort_values("event_count", ascending=False)
    acts.to_csv(out/"activity_counts.csv", index=False)
    acts.rename(columns={"activity":"stage"}).to_csv(out/"stage_metrics.csv", index=False)

    paths = df.groupby("case_id", sort=False)["activity"].agg(list)
    pc = paths.map(tuple).value_counts().rename_axis("pathway_tuple").reset_index(name="case_count")
    pc["pathway"] = pc["pathway_tuple"].map(lambda x: " -> ".join(x))
    pc["case_percent"] = pc["case_count"] / len(paths) * 100
    pc[["pathway","case_count","case_percent"]].to_csv(out/"pathway_frequencies.csv", index=False)

    df["next_activity"] = df.groupby("case_id", sort=False)["activity"].shift(-1)
    df["next_timestamp"] = df.groupby("case_id", sort=False)["timestamp"].shift(-1)
    tr = df.dropna(subset=["next_activity","next_timestamp"]).copy()
    tr["duration_minutes"] = (tr["next_timestamp"] - tr["timestamp"]).dt.total_seconds()/60
    negative = int((tr["duration_minutes"] < 0).sum())
    tr = tr[tr["duration_minutes"] >= 0]
    if len(tr):
        tm = tr.groupby(["activity","next_activity"])["duration_minutes"].agg(transition_count="size", mean_minutes="mean", median_minutes="median", p90_minutes=lambda s:s.quantile(.9), p95_minutes=lambda s:s.quantile(.95), min_minutes="min", max_minutes="max").reset_index()
        tm = tm.sort_values(["median_minutes","transition_count"], ascending=[False,False])
    else:
        tm = pd.DataFrame(columns=["activity","next_activity","transition_count","mean_minutes","median_minutes","p90_minutes","p95_minutes","min_minutes","max_minutes"])
    tm.to_csv(out/"transition_metrics.csv", index=False)
    tm[tm["transition_count"] >= 5].to_csv(out/"bottleneck_candidates.csv", index=False)

    summary = {"input_rows":int(len(raw)), "valid_event_rows":int(len(df)), "invalid_rows_excluded":invalid_rows, "case_count":int(df["case_id"].nunique()), "activity_count":int(df["activity"].nunique()), "unique_observed_pathways":int(paths.nunique()), "transition_rows":int(len(tr)), "negative_intervals_excluded":negative, "zero_minute_transitions":int((tr["duration_minutes"] == 0).sum()), "note":"Elapsed time between adjacent recorded events; not necessarily clinical waiting/service time."}
    (out/"run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    try:
        import pm4py
        ev = df[["case_id","activity","timestamp"]].rename(columns={"case_id":"case:concept:name","activity":"concept:name","timestamp":"time:timestamp"})
        ev = pm4py.format_dataframe(ev, case_id="case:concept:name", activity_key="concept:name", timestamp_key="time:timestamp")
        dfg, starts, ends = pm4py.discover_dfg(ev, case_id_key="case:concept:name", activity_key="concept:name", timestamp_key="time:timestamp")
        from pm4py.visualization.dfg import visualizer as vis
        params = {vis.Variants.FREQUENCY.value.Parameters.START_ACTIVITIES: starts, vis.Variants.FREQUENCY.value.Parameters.END_ACTIVITIES: ends}
        g = vis.apply(dfg, log=ev, variant=vis.Variants.FREQUENCY, parameters=params)
        vis.save(g, str(out/"process_map.png"))
        try:
            net, im, fm = pm4py.discover_petri_net_inductive(ev)
            pm4py.write_pnml(net, im, fm, str(out/"process_model.pnml"))
        except Exception as e:
            print(f"WARNING: Petri-net export failed: {e}", file=sys.stderr)
    except ImportError:
        print("WARNING: PM4Py is not installed; CSV analytics were generated, but process map/model were skipped.", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: PM4Py discovery failed: {e}", file=sys.stderr)
    print(json.dumps(summary, indent=2))
    print(f"Outputs: {out.resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
