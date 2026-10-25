"""Pre-flight check. Run before testing:  python preflight.py
Checks files, packages, secrets and the core logic, and prints what to fix."""
import base64
import importlib
import json
import pathlib
import py_compile
import sys

root = pathlib.Path(__file__).parent
problems, warnings = [], []


def ok(label):
    print(f"  ✓ {label}")


def fail(label, hint=""):
    problems.append(label)
    print(f"  ✗ {label}" + (f"  → {hint}" if hint else ""))


def warn(label, hint=""):
    warnings.append(label)
    print(f"  ! {label}" + (f"  → {hint}" if hint else ""))


print("Files")
for f, hint in [("app.py", ""), ("careflow_core.py", "upload it next to app.py"),
                ("careflow_pm.py", "your existing helper module must be in the same folder"),
                ("requirements.txt", ""), ("assets/careflow_mark.svg", "upload the assets folder"),
                ("assets/careflow_wordmark_aurora.svg", "upload the assets folder")]:
    (ok if (root / f).exists() else lambda l, h=hint: fail(l, h))(f if (root / f).exists() else f"missing {f}")

print("Python and packages")
if sys.version_info >= (3, 10):
    ok(f"Python {sys.version.split()[0]}")
else:
    fail(f"Python {sys.version.split()[0]} is too old", "use 3.10 or newer")
for pkg, name in [("streamlit", "streamlit"), ("pandas", "pandas"), ("numpy", "numpy"), ("plotly", "plotly"),
                  ("sklearn", "scikit-learn"), ("supabase", "supabase")]:
    try:
        m = importlib.import_module(pkg)
        ok(f"{name} {getattr(m, '__version__', '')}".strip())
        if pkg == "streamlit":
            v = tuple(int(x) for x in m.__version__.split(".")[:2] if x.isdigit())
            if v < (1, 46):
                warn("Streamlit is older than 1.46", "top navigation falls back to the sidebar; upgrade for the full design")
    except ImportError:
        fail(f"{name} is not installed", f"pip install {name}")

print("Code")
for f in ("app.py", "careflow_core.py"):
    try:
        py_compile.compile(str(root / f), doraise=True)
        ok(f"{f} compiles")
    except Exception as exc:  # noqa: BLE001
        fail(f"{f} has a syntax error", str(exc)[:120])

print("Secrets")
sec = root / ".streamlit" / "secrets.toml"
if sec.exists():
    try:
        import tomllib
        data = tomllib.loads(sec.read_text())
        for k in ("SUPABASE_URL", "SUPABASE_KEY"):
            (ok if data.get(k) else lambda l: fail(l))(f"{k} set" if data.get(k) else f"{k} missing")
        key = str(data.get("SUPABASE_KEY", ""))
        try:
            payload = json.loads(base64.urlsafe_b64decode(key.split(".")[1] + "=="))
            if payload.get("role") == "service_role":
                fail("SUPABASE_KEY is a service_role key", "use the anon key; the service key bypasses all security rules")
            else:
                ok(f"key role is '{payload.get('role')}'")
        except Exception:  # noqa: BLE001
            warn("could not read the key role", "make sure it is the anon public key")
        if not data.get("ADMIN_EMAILS"):
            warn("ADMIN_EMAILS not set", "nobody will see the Access Log page")
    except Exception as exc:  # noqa: BLE001
        fail("secrets.toml could not be read", str(exc)[:100])
else:
    warn("no local .streamlit/secrets.toml", "fine on Streamlit Cloud if you set Secrets there; see .streamlit/secrets.toml.example")

print("Core logic self-check")
try:
    sys.path.insert(0, str(root))
    import pandas as pd
    import careflow_core as core
    assert core.classify_stage("Left ED") == "transfer" and core.classify_stage("Registration") == "admission"
    sample = root / "test_kit" / "sample_event_log_SYNTHETIC.csv"
    if sample.exists():
        df = pd.read_csv(sample)
        g = core.stage_summary(df, "case_id", "activity", "timestamp")
        assert not g.empty and core.week_over_week(df, "case_id", "timestamp") is not None
        ok(f"sample data loads ({len(df):,} events, {df.case_id.nunique():,} cases)")
    else:
        warn("test_kit/sample_event_log_SYNTHETIC.csv not found")
    ok("stage logic works")
except Exception as exc:  # noqa: BLE001
    fail("core logic check failed", str(exc)[:120])

print()
if problems:
    print(f"NOT READY: {len(problems)} problem(s) to fix, {len(warnings)} warning(s).")
    sys.exit(1)
print(f"READY FOR TESTING ({len(warnings)} warning(s)). Start with TESTING.md.")
