from __future__ import annotations

import itertools
import traceback
from dataclasses import dataclass
from functools import wraps
from html import escape
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import careflow_pm as pm


st.set_page_config(page_title="CareFlow | Clinical Pathway Process Mining", page_icon="♥", layout="wide")

# ---------- CAREFLOW AUTHENTICATION ----------
from supabase import create_client

@st.cache_resource
def get_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

try:
    supabase = get_supabase_client()
except Exception:
    st.error(
        "Authentication setup error. Check SUPABASE_URL "
        "and SUPABASE_KEY in Streamlit Cloud Secrets."
    )
    st.stop()

if "careflow_user" not in st.session_state:
    st.session_state.careflow_user = None

if not st.session_state.careflow_user:
    # Login landing page inspired by the supplied reference image.
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg,#F3F4F6 0%,#E4E7EC 55%,#ffffff 100%);
        }
        [data-testid="stHeader"] { background: transparent; }
        .block-container { padding-top: 1.3rem !important; max-width: 1500px !important; }
        .cf-brand { display:flex; align-items:center; gap:14px; margin:4px 0 24px 4px; }
        .cf-logo { width:62px; height:62px; border-radius:18px; display:flex; align-items:center; justify-content:center;
                   background:linear-gradient(140deg,#1E2125,#3A3F46); color:white; font-size:39px; font-weight:800;
                   box-shadow:0 8px 24px rgba(30,33,37,.18); }
        .cf-brand-title { font-size:clamp(29px,4vw,43px); font-weight:850; letter-spacing:-1.4px; line-height:1.05;
                          color:#1E2125; }
        .cf-brand-title span { color:#E5322D; }
        .cf-brand-sub { font-size:15px; color:#5B616A; margin-top:5px; }
        .cf-topline { text-align:right; color:#3A3F46; font-size:13px; padding:15px 6px 22px; }
        .cf-login-card { background:rgba(255,255,255,.94); border:1px solid #CDD2DA; border-radius:22px;
                         padding:clamp(20px,3vw,32px); box-shadow:0 16px 42px rgba(30,33,37,.09); }
        .cf-login-title { font-size:clamp(28px,3.5vw,36px); font-weight:800; color:#1E2125; letter-spacing:-.8px; }
        .cf-login-sub { color:#5B616A; margin:4px 0 16px; font-size:15px; }
        .cf-hero { min-height:270px; border-radius:24px; padding:clamp(20px,3vw,38px); overflow:hidden;
                   background:linear-gradient(90deg,rgba(233,236,240,.98) 0%,rgba(233,236,240,.88) 44%,rgba(233,236,240,.05) 100%),
                   url('https://images.unsplash.com/photo-1551190822-a9333d879b1f?auto=format&fit=crop&w=1600&q=85') center/cover;
                   border:1px solid rgba(255,255,255,.75); box-shadow:0 14px 34px rgba(30,33,37,.08); }
        .cf-kicker { color:#E5322D; text-transform:uppercase; letter-spacing:2px; font-size:11px; font-weight:800; }
        .cf-hero-title { max-width:470px; color:#075c64; font-size:clamp(30px,4vw,44px); line-height:1.13; font-weight:850;
                         letter-spacing:-1px; margin:12px 0; }
        .cf-hero-title span { color:#E5322D; }
        .cf-hero-copy { max-width:390px; color:#4A5058; font-size:15px; line-height:1.65; }
        .cf-feature-row { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:18px 0; }
        .cf-feature { text-align:center; color:#2F3338; font-size:12px; line-height:1.4; }
        .cf-feature-icon { width:54px; height:54px; margin:0 auto 7px; border-radius:50%; background:#DDE1E7;
                           display:flex; align-items:center; justify-content:center; font-size:24px; }
        .cf-photo-caption { font-size:12px; color:#3A3F46; font-weight:650; padding-top:4px; }
        [data-testid="stImage"] img { border-radius:14px; object-fit:cover; }
        div[data-testid="stFormSubmitButton"] button { background:linear-gradient(100deg,#2F3338,#3A3F46) !important;
          color:white !important; border:0 !important; border-radius:999px !important; min-height:48px; font-weight:750 !important; }
        div[data-testid="stTextInput"] input { border-radius:10px !important; border-color:#B4BAC3 !important; }
        button[data-baseweb="tab"] { color:#5B616A !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color:#E5322D !important; }
        @media (max-width: 700px) {
          .cf-topline { text-align:left; padding:0 4px 12px; }
          .cf-feature-row { grid-template-columns:repeat(2,minmax(0,1fr)); }
          .cf-hero { min-height:220px; }
        }
        </style>
        <div class="cf-brand">
          <div class="cf-logo">♥</div>
          <div><div class="cf-brand-title">Care<span>Flow</span></div>
          <div class="cf-brand-sub">Clinical Pathway Process Mining</div></div>
        </div>
        <div class="cf-topline">Better Insights &nbsp; · &nbsp; Smoother Pathways &nbsp; · &nbsp; Healthier Tomorrows</div>
        """,
        unsafe_allow_html=True,
    )

    login_col, hero_col = st.columns([0.88, 1.42], gap="large", vertical_alignment="top")

    with login_col:
        st.markdown(
            '<div class="cf-login-card"><div class="cf-login-title">Welcome Back</div>'
            '<div class="cf-login-sub">Sign in to access your clinical analytics workspace.</div></div>',
            unsafe_allow_html=True,
        )
        login_tab, signup_tab = st.tabs(["Login", "Create new account"])

        with login_tab:
            with st.form("careflow_login_form"):
                login_email = st.text_input("✉ Email address", placeholder="you@example.com")
                login_password = st.text_input("♙ Password", type="password", placeholder="Enter your password")
                login_submit = st.form_submit_button("Login  →", use_container_width=True)
            if login_submit:
                try:
                    result = supabase.auth.sign_in_with_password({
                        "email": login_email.strip(), "password": login_password
                    })
                    if result.session and result.user:
                        st.session_state.careflow_user = {"id": result.user.id, "email": result.user.email}
                        st.rerun()
                    else:
                        st.error("Login unsuccessful. Please try again.")
                except Exception:
                    st.error("Login failed. Check your email and password or verify your email address.")

        with signup_tab:
            with st.form("careflow_signup_form"):
                signup_email = st.text_input("✉ Email address", placeholder="you@example.com", key="signup_email")
                signup_password = st.text_input("♙ Create password", type="password", key="signup_password")
                confirm_password = st.text_input("♙ Confirm password", type="password", key="confirm_password")
                signup_submit = st.form_submit_button("Create account", use_container_width=True)
            if signup_submit:
                if not signup_email.strip():
                    st.error("Enter your email address.")
                elif len(signup_password) < 8:
                    st.error("Use a password of at least 8 characters.")
                elif signup_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        result = supabase.auth.sign_up({"email": signup_email.strip(), "password": signup_password})
                        if result.session and result.user:
                            st.session_state.careflow_user = {"id": result.user.id, "email": result.user.email}
                            st.success("Account created successfully.")
                            st.rerun()
                        else:
                            st.success("Registration received. Check your email to verify your account, then log in.")
                    except Exception:
                        st.error("Signup failed. Check your email, password requirements, and Supabase authentication settings.")

        st.markdown(
            '<div style="text-align:center;color:#5B616A;font-size:12px;padding:12px 4px;">'
            '♢ Secure access &nbsp; · &nbsp; Your account and data are protected</div>',
            unsafe_allow_html=True,
        )

    with hero_col:
        st.markdown(
            '<div class="cf-hero"><div class="cf-kicker">Clinical intelligence for better care</div>'
            '<div class="cf-hero-title">Transforming Patient Flow with <span>Data-Driven Insights</span></div>'
            '<div class="cf-hero-copy">CareFlow helps healthcare teams analyze clinical pathways, improve coordination, '
            'and support better operational decisions.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="cf-feature-row">'
            '<div class="cf-feature"><div class="cf-feature-icon">▥</div>Clinical<br>Analytics</div>'
            '<div class="cf-feature"><div class="cf-feature-icon">⌘</div>Pathway<br>Analysis</div>'
            '<div class="cf-feature"><div class="cf-feature-icon">▤</div>Reports &<br>Insights</div>'
            '<div class="cf-feature"><div class="cf-feature-icon">♢</div>Governance<br>& Security</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        equipment_cols = st.columns(3, gap="small")
        medical_photos = [
            ("https://images.unsplash.com/photo-1584982751601-97dcc096659c?auto=format&fit=crop&w=700&q=80", "Clinical care"),
            ("https://images.unsplash.com/photo-1511174511562-5f7f18b874f8?auto=format&fit=crop&w=700&q=80", "Medical equipment"),
            ("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=700&q=80", "Healthcare team"),
        ]
        for photo_col, (photo_url, photo_caption) in zip(equipment_cols, medical_photos):
            with photo_col:
                st.image(photo_url, use_container_width=True)
                st.markdown(f'<div class="cf-photo-caption">{photo_caption}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align:right;color:#E5322D;font-style:italic;font-weight:700;'
            'font-size:18px;padding:12px 8px;">Smarter care starts with better data.</div>',
            unsafe_allow_html=True,
        )

    st.stop()

# ---------- END CAREFLOW AUTHENTICATION ----------

st.markdown("""
<style>
:root {
  --cf-ivory: #E9ECF0;
  --cf-ivory-card: #F7F8FA;
  --cf-emerald: #2F3338;
  --cf-emerald-dark: #1E2125;
  --cf-vermillion: #E5322D;
  --cf-ink: #171717;
  --cf-muted: #5B616A;
  --cf-border: #CDD2DA;
}
.block-container {
  width: 100%; max-width: 1640px;
  padding-top: 1.15rem; padding-left: clamp(.75rem, 2.2vw, 2.2rem);
  padding-right: clamp(.75rem, 2.2vw, 2.2rem); padding-bottom: 2.5rem;
}
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #E9ECF0 0%, #E9ECF0 100%) !important;
  color: var(--cf-ink) !important;
}
[data-testid="stHeader"] { background: rgba(233,236,240,.94) !important; }
/* Full emerald sidebar: include nested Streamlit containers so no white panels remain */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] [data-testid="stSidebarContent"],
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
[data-testid="stSidebar"] [data-testid="stElementContainer"],
[data-testid="stSidebar"] [data-testid="stBottom"],
[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: linear-gradient(180deg, #1E2125 0%, #2F3338 100%) !important;
}
[data-testid="stSidebar"] {
  background-color: #2F3338 !important;
  border-right: 3px solid var(--cf-vermillion) !important;
}
[data-testid="stSidebar"] * { color: var(--cf-ivory) !important; }
[data-testid="stSidebar"] button {
  background: rgba(233,236,240,.08) !important; color: var(--cf-ivory) !important;
  border: 1px solid rgba(233,236,240,.2) !important; border-radius: 12px !important;
}
[data-testid="stSidebar"] button:hover { background: rgba(229,50,45,.18) !important; border-color: var(--cf-vermillion) !important; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 7px; }
[data-testid="stSidebar"] [role="radiogroup"] label,
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  background: transparent !important; border: 1px solid transparent !important;
  border-radius: 10px !important; padding: 8px 10px !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover,
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #3A3F46 !important; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked),
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked),
[data-testid="stSidebar"] [aria-checked="true"] {
  background: var(--cf-vermillion) !important; border-color: var(--cf-vermillion) !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(233,236,240,.25) !important; }
.hero {
  position: relative; padding: clamp(1.2rem, 2.8vw, 2rem); border-radius: 22px;
  background: linear-gradient(115deg, #1E2125 0%, #2F3338 72%, #E5322D 100%) !important;
  color: #fff; margin: .2rem 0 1.25rem; overflow: hidden;
  box-shadow: 0 12px 32px rgba(30,33,37,.13); border: 1px solid rgba(255,255,255,.18);
}
.hero h1, .hero h2 { color: #FFFFFF !important; }
.hero p { color: #E9ECF0 !important; margin: .55rem 0 0; font-size: clamp(.88rem, 1.4vw, 1.02rem); }
h1, h2, h3, h4 { color: var(--cf-emerald-dark) !important; letter-spacing: -.02em; overflow-wrap: anywhere; }
p, label, [data-testid="stMarkdownContainer"] { color: var(--cf-ink); }
hr { border-color: var(--cf-border) !important; }
.metric-card, .cf-feature-card, [data-testid="stMetric"],
[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--cf-border) !important; border-radius: 16px !important;
  background: linear-gradient(145deg, #F7F8FA 0%, #E9ECF0 100%) !important;
  box-shadow: 0 5px 18px rgba(30,33,37,.06) !important;
}
.metric-card { padding: 1.1rem 1.15rem; position: relative; overflow: hidden; }
.metric-card:before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--cf-vermillion); }
.metric-label, .cf-feature-copy, [data-testid="stMetric"] label { color: var(--cf-muted) !important; }
.metric-value, .cf-feature-title, [data-testid="stMetricValue"] { color: var(--cf-emerald) !important; font-weight: 800 !important; }
[data-testid="stPlotlyChart"] { background: var(--cf-ivory-card) !important; border: 1px solid var(--cf-border) !important; border-radius: 14px !important; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--cf-border) !important; border-radius: 13px !important; overflow: hidden; }
[data-testid="stExpander"] { border: 1px solid var(--cf-border) !important; border-radius: 14px !important; background: var(--cf-ivory-card) !important; }
[data-testid="stCaptionContainer"] { color: var(--cf-muted) !important; }
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
  background: var(--cf-emerald) !important; color: #FFFFFF !important;
  border: 1px solid var(--cf-emerald) !important; border-radius: 12px !important; font-weight: 700 !important;
}
.stButton button:hover, .stDownloadButton button:hover,
[data-testid="stFormSubmitButton"] button:hover { background: var(--cf-vermillion) !important; border-color: var(--cf-vermillion) !important; }
[data-baseweb="input"] > div, [data-baseweb="textarea"] > div,
[data-baseweb="select"] > div { border-color: #B4BAC3 !important; background: #F7F8FA !important; }
[data-baseweb="input"] > div:focus-within, [data-baseweb="textarea"] > div:focus-within { border-color: var(--cf-emerald) !important; box-shadow: 0 0 0 2px rgba(47,51,56,.12) !important; }
[data-baseweb="tab-list"] { background: #DDE1E7 !important; border-radius: 12px !important; }
[data-baseweb="tab"] { color: var(--cf-ink) !important; }
[data-baseweb="tab"][aria-selected="true"] { color: var(--cf-emerald) !important; }
[data-testid="stAlert"] { border-radius: 13px; }
.cf-feature-title { font-size: 1.02rem; margin-bottom: 7px; }
.cf-feature-copy { font-size: .88rem; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ======================================================================
# EXTRA UI STYLES (navigation, sidebar widgets, badges)
# ======================================================================
st.markdown("""
<style>
/* sidebar navigation (st.navigation) */
[data-testid="stSidebarNav"] a, [data-testid="stSidebarNavLink"] { border-radius: 10px !important; }
[data-testid="stSidebarNav"] a[aria-current="page"], [data-testid="stSidebarNavLink"][aria-current="page"] {
  background: var(--cf-vermillion) !important; }
[data-testid="stSidebarNavSeparator"], [data-testid="stSidebarNav"] span[class*="Header"] { opacity: .75; }
/* inputs inside the dark sidebar must stay readable */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div { background: #F7F8FA !important; }
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="input"] *,
[data-testid="stSidebar"] input { color: #171717 !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] { background: #E5322D !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] * { color: #fff !important; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
  background: rgba(233,236,240,.10) !important; border: 1px dashed rgba(233,236,240,.4) !important; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * { color: #E9ECF0 !important; }
/* status line under each page header */
.cf-status { display:flex; flex-wrap:wrap; gap:8px; margin:-.4rem 0 1rem; }
.cf-chip { background:#F7F8FA; border:1px solid #CDD2DA; color:#4A5058; border-radius:999px;
           padding:3px 12px; font-size:.78rem; }
.cf-chip.warn { background:#FDEBE7; border-color:#E5322D; color:#8A2A1B; }
.cf-source { color:#5B616A; font-size:.8rem; margin:-.3rem 0 .6rem; }
</style>
""", unsafe_allow_html=True)

# ======================================================================
# THEME + SMALL UI HELPERS
# ======================================================================
# CareFlow patient-journey palette: keep stage meanings consistent across pages.
STAGE_COLORS = {
    "admission": "#0F766E",      # registration / admission
    "diagnostics": "#0284C7",    # assessment / diagnostics
    "treatment": "#6366F1",      # treatment / procedure
    "completed": "#16A34A",      # discharge / completed
    "waiting": "#D97706",        # waiting / delay
    "attention": "#DC2626",      # exception / attention required
    "other": "#64748B",          # unclassified activity
}
PALETTE = [STAGE_COLORS["admission"], STAGE_COLORS["diagnostics"],
           STAGE_COLORS["treatment"], STAGE_COLORS["completed"],
           STAGE_COLORS["waiting"], STAGE_COLORS["attention"], "#155E75", "#94A3B8"]

def activity_stage_color(activity):
    """Map recorded activity labels to a visual stage; this is not clinical triage."""
    label = str(activity).strip().lower()
    rules = [
        ("completed", ("discharg", "complete", "completed", "depart", "end of care", "follow-up complete")),
        ("waiting", ("wait", "pending", "queue", "hold", "delay", "await")),
        ("attention", ("exception", "error", "cancel", "cancell", "rework", "escalat", "failed", "failure")),
        ("diagnostics", ("diagnos", "test", "lab", "laboratory", "scan", "imaging", "assessment", "investigat", "triage", "exam")),
        ("treatment", ("treat", "medicat", "therapy", "procedure", "surgery", "operation", "intervention", "prescri")),
        ("admission", ("admi", "register", "arrival", "intake", "check-in", "check in", "enrol", "enroll")),
    ]
    for stage, keywords in rules:
        if any(word in label for word in keywords):
            return STAGE_COLORS[stage]
    return STAGE_COLORS["other"]

pio.templates["careflow"] = go.layout.Template(layout=go.Layout(
    colorway=PALETTE, font=dict(color="#172B4D"),
    paper_bgcolor="#F7FAFC", plot_bgcolor="#F7FAFC",
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor="#E2E8F0", zerolinecolor="#CBD5E1"),
    yaxis=dict(gridcolor="#E2E8F0", zerolinecolor="#CBD5E1"),
))
pio.templates.default = "careflow"
px.defaults.template = "careflow"
px.defaults.color_continuous_scale = ["#DDF4F1", "#0F766E"]

# Streamlit >= 1.50 replaces use_container_width with width="stretch".
try:
    _ST_VERSION = tuple(int(x) for x in st.__version__.split(".")[:2])
except Exception:
    _ST_VERSION = (0, 0)
WIDE = {"width": "stretch"} if _ST_VERSION >= (1, 50) else {"use_container_width": True}

_chart_ids = itertools.count()  # reset on every script run -> stable, unique chart keys


def table(data, **kw):
    st.dataframe(data, hide_index=True, **WIDE, **kw)


def chart(build, empty="Not enough data to draw this chart.", height=None):
    """Render a Plotly figure from build(); never lets a bad chart break the page.
    build() returns a figure, or None when there is nothing to draw."""
    try:
        fig = build()
    except Exception as exc:  # noqa: BLE001 - surface any charting problem gracefully
        st.warning("This chart could not be drawn. The rest of the page is unaffected.")
        with st.expander("Technical details"):
            st.code(f"{type(exc).__name__}: {exc}")
        return
    if fig is None:
        st.info(empty)
        return
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, theme=None, key=f"cf_chart_{next(_chart_ids)}",
                    config={"displaylogo": False}, **WIDE)


def status_chips():
    if C.raw.empty:
        return
    chips = [f"{len(C.f):,} of {len(C.raw):,} events", f"{C.n_cases:,} cases", f"Source: {C.source}"]
    if C.active:
        chips.append("Filters: " + C.active)
    html = "".join(f'<span class="cf-chip">{escape(c)}</span>' for c in chips)
    if C.synthetic:
        html += '<span class="cf-chip warn">Departments are synthetic demo labels</span>'
    st.markdown(f'<div class="cf-status">{html}</div>', unsafe_allow_html=True)


def page_header(title, subtitle="Turn event-log data into clearer operational insights and pathway visibility.",
                chips=True):
    st.markdown(
        '<div class="hero"><div style="font-size:.72rem;letter-spacing:.15em;font-weight:800;color:#C9CED6;'
        'margin-bottom:.55rem">CLINICAL ANALYTICS WORKSPACE</div>'
        f'<h1>CareFlow <span style="font-weight:450;font-size:clamp(.95rem,2vw,1.15rem);opacity:.92">/ {title}</span></h1>'
        f"<p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )
    if chips:
        status_chips()


def kpis(items):
    for col, (label, value) in zip(st.columns(len(items)), items):
        col.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div></div>',
            unsafe_allow_html=True,
        )


def fmt_hours(x):
    return "—" if x is None or pd.isna(x) else f"{x:,.1f} h"


def source_note(text):
    st.markdown(f'<div class="cf-source">Source: {text}</div>', unsafe_allow_html=True)


def footer():
    st.divider()
    st.caption(
        "CareFlow is a clinical process analytics workspace, not a clinical decision-support system. "
        "Department labels are synthetic where indicated. Do not publish identifiable patient or health data "
        "to a public repository."
    )


def guard(fn):
    """Wrap a page so an unexpected error shows a friendly message instead of a crash.
    (st.stop / st.rerun derive from BaseException and pass straight through.)"""
    @wraps(fn)
    def inner():
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            st.error("This page ran into a problem and could not finish loading. "
                     "Other pages are unaffected. Try adjusting the filters, or check Field mapping in the sidebar.")
            with st.expander("Technical details"):
                st.code(f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}")
        footer()
    return inner


def need(**roles):
    """need(**{"case ID": C.case}) -> True if all mapped, else shows guidance."""
    missing = [label for label, col in roles.items() if not col]
    if missing:
        st.info(f"This view needs: {', '.join(missing)}. Assign them under **Field mapping** in the sidebar. "
                f"Detected fields: {', '.join(map(str, C.raw.columns))}")
        return False
    return True


# ======================================================================
# DATA LAYER (cached, with loading states)
# ======================================================================
EVENT_LOG_CANDIDATES = ["careflow_event_log.csv", "event_log_ED_MMA_2026.csv", "sample_event_log.csv"]
PM_OUTPUT_DIRS = ["pm_outputs", "process_mining_outputs", "."]
PM_OUTPUT_KEYS = {"transitions": ["transition", "dfg", "directly_follows"], "variants": ["variant", "pathway"]}
PM_NORMALIZERS = {"transitions": pm.normalize_transitions, "variants": pm.normalize_variants}


@st.cache_data(show_spinner=False)
def _read_csv(path, mtime):
    return pd.read_csv(path)


def load_event_log(uploaded):
    """-> (DataFrame, source label, error message or None)"""
    if uploaded is not None:
        try:
            d = pd.read_csv(uploaded)
            return d, uploaded.name, (None if not d.empty else "The uploaded file has no rows.")
        except Exception as exc:  # noqa: BLE001
            return pd.DataFrame(), uploaded.name, f"Could not read the uploaded file ({type(exc).__name__}: {exc})."
    problems = []
    for name in EVENT_LOG_CANDIDATES:
        p = Path(name)
        if not p.exists():
            continue
        try:
            d = _read_csv(str(p), p.stat().st_mtime)
            if not d.empty:
                return d, name, None
            problems.append(f"{name} is empty")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{name}: {type(exc).__name__}")
    return pd.DataFrame(), "No CSV found", "; ".join(problems) or None


def discover_pm_outputs():
    """Look for process-mining CSV outputs and normalise them. Never raises."""
    found, notes = {}, []
    for folder in PM_OUTPUT_DIRS:
        p = Path(folder)
        if not p.is_dir():
            continue
        for f in sorted(p.glob("*.csv")):
            stem = f.stem.lower()
            for kind, keys in PM_OUTPUT_KEYS.items():
                if kind in found or not any(k in stem for k in keys):
                    continue
                try:
                    norm = PM_NORMALIZERS[kind](_read_csv(str(f), f.stat().st_mtime))
                except Exception as exc:  # noqa: BLE001
                    notes.append(f"{f.name}: could not be read ({type(exc).__name__})")
                    continue
                if norm is None:
                    notes.append(f"{f.name}: columns not recognised as {kind}")
                else:
                    found[kind] = {"file": f.name, "data": norm}
    return found, notes


@st.cache_data(show_spinner="Preparing event log…")
def prepare_log(raw, case, time, dept):
    d = raw.copy()
    if time:
        d[time] = pm.parse_timestamps(d[time])
    synthetic = False
    if not dept:
        d = pm.add_demo_department(d, case or d.columns[0])
        dept, synthetic = "demo_department", True
    return d, dept, synthetic


@st.cache_data(show_spinner="Mining directly-follows transitions…")
def cached_transitions(d, case, act, time):
    return pm.mine_transitions(d, case, act, time)


@st.cache_data(show_spinner="Building pathway variants…")
def cached_variants(d, case, act, time):
    return pm.mine_variants(d, case, act, time)


@st.cache_data(show_spinner="Calculating case durations…")
def cached_durations(d, case, time):
    return pm.case_durations(d, case, time)


def pm_source(kind, label, compute):
    """Use a precomputed process-mining output if one exists and the user opts in; else compute live."""
    pre = C.pm_outputs.get(kind)
    if pre and st.toggle(f"Use precomputed {label} ({pre['file']}) — ignores filters", key=f"use_pre_{kind}"):
        return pre["data"], f"precomputed process-mining output · {pre['file']}"
    return compute(), "computed live from the filtered event log"


@dataclass
class Ctx:
    raw: pd.DataFrame          # prepared, unfiltered
    f: pd.DataFrame            # filtered
    source: str
    case: Optional[str]
    act: Optional[str]
    time: Optional[str]
    dept: Optional[str]
    status: Optional[str]
    staff: Optional[str]
    synthetic: bool
    pm_outputs: dict
    dept_summary: str
    active: str = ""

    @property
    def n_cases(self):
        return int(self.f[self.case].nunique()) if self.case else len(self.f)


C: Ctx  # assigned once data + filters are ready (below)


def top_counts(series, label, top=10):
    return series.fillna("Unknown").astype(str).value_counts().head(top).rename_axis(label).reset_index(name="Events")


def fig_bar_counts(col, label, top=10, height=300):
    if not col:
        return None
    d = top_counts(C.f[col], label, top)
    if d.empty:
        return None
    fig = px.bar(d, x="Events", y=label, orientation="h")
    fig.update_traces(marker_color=PALETTE[0])
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=height, showlegend=False)
    return fig


def fig_donut(col, label, height=300):
    if not col:
        return None
    d = top_counts(C.f[col], label, 6)
    if d.empty:
        return None
    fig = px.pie(d, names=label, values="Events", hole=0.58)
    fig.update_layout(height=height, legend=dict(orientation="h", y=-0.1))
    return fig


FREQ = {"Day": "D", "Week": "W", "Month": "MS"}


def fig_volume(grain, height=300):
    if not C.time:
        return None
    t = C.f.dropna(subset=[C.time])
    if t.empty:
        return None
    s = t.groupby(pd.Grouper(key=C.time, freq=FREQ[grain])).size().reset_index(name="Events")
    fig = px.area(s, x=C.time, y="Events")
    fig.update_traces(line_color=PALETTE[1], fillcolor="rgba(229,50,45,.25)")
    fig.update_layout(height=height, xaxis_title=None)
    return fig


def pick_top(n_total, label, key, default=10, cap=30):
    if n_total <= 3:
        return n_total
    return st.slider(label, 3, min(cap, n_total), min(default, n_total), key=key)


# ======================================================================
# PAGES
# ======================================================================
@guard
def page_dashboard():
    page_header("Executive Dashboard")
    f = C.f
    dur = cached_durations(f, C.case, C.time) if C.case and C.time else pd.DataFrame()
    median_h = dur["Elapsed hours"].median() if not dur.empty else float("nan")
    kpis([
        ("Cases / patients", f"{C.n_cases:,}"),
        ("Event records", f"{len(f):,}"),
        ("Unique activities", f"{f[C.act].nunique():,}" if C.act else "—"),
        ("Departments", f"{f[C.dept].nunique():,}"),
        ("Median elapsed time", fmt_hours(median_h)),
    ])
    st.write("")
    grain = st.radio("Group event volume by", list(FREQ), horizontal=True, key="dash_grain")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Activity distribution**")
        chart(lambda: fig_bar_counts(C.act, "Activity", 8), "No activity column is mapped.")
    with c2:
        st.markdown("**Department workload**")
        chart(lambda: fig_donut(C.dept, "Department"))
    with c3:
        st.markdown("**Event volume over time**")
        chart(lambda: fig_volume(grain), "A parseable timestamp column is needed for this chart.")
    l, r = st.columns([1, 1])
    with l:
        st.markdown("**Case elapsed-time distribution**")
        chart(lambda: None if dur.empty else px.histogram(dur, x="Elapsed hours", nbins=30)
              .update_traces(marker_color=PALETTE[0]).update_layout(height=300),
              "Needs case IDs and parseable timestamps.")
    with r:
        st.markdown("**Event log preview**")
        table(f.head(12))


@guard
def page_pm_explorer():
    page_header("Process Mining Explorer")
    st.caption("Observed event sequences from the selected event log. This describes recorded workflow; "
               "it does not recommend clinical treatment.")
    if not need(**{"case ID": C.case, "activity": C.act}):
        return
    tab_map, tab_wait, tab_var = st.tabs(["Transition map", "Bottlenecks", "Variants"])

    trans, trans_src = pm_source("transitions", "transitions",
                                 lambda: cached_transitions(C.f, C.case, C.act, C.time))
    with tab_map:
        source_note(trans_src)
        if trans.empty:
            st.info("There are not enough consecutive events within a case to calculate transitions.")
        else:
            n_acts = len(set(trans["From activity"]) | set(trans["To activity"]))
            n = pick_top(n_acts, "Activities shown in the map", "pm_map_n", default=12)

            def heatmap():
                involvement = pd.concat([trans.groupby("From activity")["Transitions"].sum(),
                                         trans.groupby("To activity")["Transitions"].sum()]).groupby(level=0).sum()
                keep = involvement.nlargest(n).index
                sub = trans[trans["From activity"].isin(keep) & trans["To activity"].isin(keep)]
                m = sub.pivot_table(index="From activity", columns="To activity", values="Transitions",
                                    aggfunc="sum", fill_value=0)
                fig = px.imshow(m, aspect="auto", text_auto=True,
                                labels=dict(x="To activity", y="From activity", color="Transitions"))
                fig.update_layout(height=140 + 32 * len(m))
                return fig
            chart(heatmap)
            st.caption("Rows are the activity that happened first; columns are what directly followed it.")
            table(trans.head(200))
            st.download_button("Export transitions CSV", trans.to_csv(index=False).encode("utf-8"),
                               "careflow_transitions.csv", "text/csv")
    with tab_wait:
        source_note(trans_src)
        if "Avg wait (h)" not in trans.columns or trans.empty:
            st.info("Waiting times need a parseable timestamp column (or an output file with an hours-based wait column).")
        else:
            min_n = st.slider("Minimum transitions to include", 1, int(max(trans["Transitions"].max(), 2)), 1,
                              key="pm_wait_min")

            def waits():
                w = trans[trans["Transitions"] >= min_n].nlargest(15, "Avg wait (h)").copy()
                if w.empty:
                    return None
                w["Step"] = w["From activity"] + " → " + w["To activity"]
                fig = px.bar(w, x="Avg wait (h)", y="Step", orientation="h", hover_data=["Transitions"])
                fig.update_traces(marker_color=PALETTE[1])
                fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=140 + 28 * len(w))
                return fig
            chart(waits, "No transitions meet the minimum count.")
            st.caption("Longest average gaps between consecutive recorded events. Long waits can reflect "
                       "documentation delays as well as real queues.")
    with tab_var:
        render_variants(key="pm")


def render_variants(key):
    variants, src = pm_source("variants", "variants", lambda: cached_variants(C.f, C.case, C.act, C.time)[0])
    source_note(src)
    if variants.empty:
        st.info("No complete pathways could be assembled from the current filters.")
        return
    c1, c2 = st.columns([2, 1])
    with c1:
        query = st.text_input("Search pathways by activity name", key=f"{key}_variant_q")
    with c2:
        st.metric("Distinct pathways", f"{len(variants):,}")
    shown = variants
    if query.strip():
        shown = variants[variants["Observed pathway"].str.contains(query.strip(), case=False, regex=False)]
    if shown.empty:
        st.info("No pathway contains that text.")
        return
    n = pick_top(len(shown), "Pathways to chart", f"{key}_variant_n", default=10)
    top = shown.head(n)

    def bar():
        fig = px.bar(top, x="Cases", y="Variant", orientation="h",
                     hover_data=["Observed pathway", "Share of cases (%)", "Steps"])
        fig.update_traces(marker_color=PALETTE[0])
        fig.update_layout(yaxis={"autorange": "reversed"}, height=120 + 30 * len(top))
        return fig
    chart(bar)
    table(shown.head(200))
    st.download_button("Export pathways CSV", shown.to_csv(index=False).encode("utf-8"),
                       "careflow_pathways.csv", "text/csv", key=f"{key}_variant_dl")


@guard
def page_patient_flow():
    page_header("Patient Flow")
    if not need(**{"case ID": C.case, "activity": C.act}):
        return
    tab_case, tab_time = st.tabs(["Case timeline", "Elapsed time"])
    with tab_case:
        ids = C.f[C.case].dropna().astype(str).unique()
        if len(ids) == 0:
            st.info("No cases in the current filters.")
        else:
            if len(ids) > 5000:
                st.caption("Showing the first 5,000 cases; narrow the filters to reach others.")
            choice = st.selectbox("Select a case", ids[:5000], key="flow_case")
            ev = C.f[C.f[C.case].astype(str) == choice].copy()
            if C.time:
                ev = ev.sort_values(C.time, kind="stable")
            ev["Step"] = range(1, len(ev) + 1)
            ev[C.act] = ev[C.act].fillna("Unknown activity").astype(str)

            def timeline():
                use_time = bool(C.time) and ev[C.time].notna().any()
                fig = px.line(ev, x=C.time if use_time else "Step", y=C.act, markers=True, hover_data=["Step"])
                # Color each recorded activity by its mapped patient-journey stage.
                marker_colors = [activity_stage_color(a) for a in ev[C.act]]
                fig.update_traces(line=dict(color="#94A3B8", width=2),
                                  marker=dict(size=10, color=marker_colors,
                                              line=dict(color="#FFFFFF", width=1)))
                fig.update_yaxes(categoryorder="array", categoryarray=list(dict.fromkeys(ev[C.act])),
                                 autorange="reversed", title=None)
                fig.update_layout(height=140 + 34 * ev[C.act].nunique())
                return fig
            chart(timeline)
            legend_cols = st.columns(3)
            legend_items = [("Admission / registration", STAGE_COLORS["admission"]),
                            ("Assessment / diagnostics", STAGE_COLORS["diagnostics"]),
                            ("Treatment", STAGE_COLORS["treatment"]),
                            ("Discharge / completed", STAGE_COLORS["completed"]),
                            ("Waiting / delay", STAGE_COLORS["waiting"]),
                            ("Exception / attention", STAGE_COLORS["attention"])]
            for i, (label, color) in enumerate(legend_items):
                with legend_cols[i % 3]:
                    st.markdown(f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{color};margin-right:7px"></span>{escape(label)}', unsafe_allow_html=True)
            st.caption("Colors are inferred from recorded activity names for navigation only; verify mappings for your event log. They do not indicate clinical severity or outcomes.")
            st.caption("Events are ordered by timestamp when available, otherwise by file order.")
            table(ev.drop(columns=["Step"]))
    with tab_time:
        if not need(**{"timestamp": C.time}):
            return
        dur = cached_durations(C.f, C.case, C.time)
        if dur.empty:
            st.info("No cases with usable timestamps.")
            return
        a, b, c = st.columns(3)
        a.metric("Cases with timestamps", f"{len(dur):,}")
        b.metric("Median elapsed", fmt_hours(dur["Elapsed hours"].median()))
        c.metric("90th percentile", fmt_hours(dur["Elapsed hours"].quantile(0.9)))
        chart(lambda: px.histogram(dur, x="Elapsed hours", nbins=30).update_traces(marker_color=PALETTE[0]))
        st.caption("Elapsed time is the span between first and last recorded event, not necessarily length of stay.")
        st.markdown("**Longest observed cases**")
        table(dur.nlargest(20, "Elapsed hours").round({"Elapsed hours": 2}))


@guard
def page_pathways():
    page_header("Clinical Pathways")
    if not need(**{"case ID": C.case, "activity": C.act}):
        return
    render_variants(key="cp")
    st.caption("These are observed sequences from the supplied event log, not clinical recommendations.")


@guard
def page_comparison():
    page_header("Pathway Comparison")
    st.caption("Descriptive comparison of observed pathways. Always computed from the filtered event log.")
    if not need(**{"case ID": C.case, "activity": C.act}):
        return
    variants, seq = cached_variants(C.f, C.case, C.act, C.time)
    if variants.empty:
        st.info("No complete pathways could be assembled from the current filters.")
        return
    head = variants.head(50)
    labels = {v: f"{v} · {n} cases · {p[:70]}"
              for v, n, p in zip(head["Variant"], head["Cases"], head["Observed pathway"])}
    picked = st.multiselect("Pathways to compare (up to 5)", list(labels), default=list(labels)[:3],
                            format_func=labels.get, max_selections=5, key="cmp_pick")
    if len(picked) < 2:
        st.info("Select at least two pathways.")
        return
    sel = variants[variants["Variant"].isin(picked)].copy()
    if C.time:
        dur = cached_durations(C.f, C.case, C.time).merge(seq.rename("Observed pathway"), left_on=C.case, right_index=True)
        med = dur.groupby("Observed pathway")["Elapsed hours"].median().round(1).rename("Median elapsed (h)")
        sel = sel.merge(med, on="Observed pathway", how="left")
    c1, c2 = st.columns(2)
    with c1:
        chart(lambda: px.bar(sel, x="Variant", y="Cases", hover_data=["Observed pathway"]).update_traces(marker_color=PALETTE[0]),
              height=320)
    with c2:
        chart(lambda: px.bar(sel, x="Variant", y="Median elapsed (h)", hover_data=["Observed pathway"])
              .update_traces(marker_color=PALETTE[1]) if "Median elapsed (h)" in sel else None,
              "Median elapsed time needs a parseable timestamp column.", height=320)
    table(sel)
    if len(picked) == 2:
        a, b = (set(sel.loc[sel["Variant"] == v, "Observed pathway"].iloc[0].split(" → ")) for v in picked)
        d1, d2 = st.columns(2)
        d1.markdown(f"**Only in {picked[0]}:** " + (", ".join(sorted(a - b)) or "—"))
        d2.markdown(f"**Only in {picked[1]}:** " + (", ".join(sorted(b - a)) or "—"))


@guard
def page_beds():
    page_header("Bed & Discharge Management")
    st.caption("Operational indicators appear only when the event log contains suitable fields. No bed availability is invented.")
    raw = C.raw
    bed = pm.find_col(raw, ["bed status", "bed availability", "bed id", "bed number", "bed occupied"])
    disch = pm.find_col(raw, ["discharge", "discharged at", "discharge date", "discharge time"])
    adm = pm.find_col(raw, ["admission", "admitted at", "admission date", "admission time"])
    a, b, c = st.columns(3)
    a.metric("Cases in current filter", f"{C.n_cases:,}")
    b.metric("Admission field", "Available" if adm else "Not detected")
    c.metric("Discharge field", "Available" if disch else "Not detected")
    if bed:
        counts = top_counts(C.f[bed], "Recorded value", 30).rename(columns={"Events": "Records"})
        chart(lambda: px.bar(counts, x="Recorded value", y="Records", title="Recorded bed-related values"))
    else:
        st.info("No bed/occupancy field was detected, so occupancy and available-bed counts cannot be calculated.")
    if adm or disch:
        cols = [c for c in [C.case, adm, disch, C.dept, C.status] if c]
        table(C.f[cols].drop_duplicates().head(500))
    else:
        st.info("Add verified admission/discharge timestamps to the source data to enable discharge-delay analysis.")
    st.warning("This is an analytics view, not a live bed-management system. Confirm all operational figures "
               "against the hospital's authoritative system.")


@guard
def page_coordination():
    page_header("Care coordination")
    st.write("Department-level overview based on the available fields.")
    if C.synthetic:
        st.warning("Departments here are synthetic demo labels, not source data.")
    d = top_counts(C.f[C.dept], "Department", 50).rename(columns={"Events": "Event records"})
    table(d)
    chart(lambda: px.bar(d, x="Department", y="Event records").update_traces(marker_color=PALETTE[0]))


_TEAM_HINTS = ("zone", "unit", "ward", "service", "consult", "department", "triage", "disposition", "team", "clinic")
_TEAM_SKIP = ("month", "day", "age", "timestamp", "time", "date")


def _team_columns():
    """Low-cardinality fields that can stand in for care units / services when no staff column exists."""
    cols = []
    for col in C.f.columns:
        name = str(col).lower()
        if col in (C.case, C.time, C.act) or any(name == k or name.endswith("_" + k) for k in _TEAM_SKIP):
            continue
        n = C.f[col].nunique(dropna=True)
        if 2 <= n <= 40:
            cols.append(col)
    cols.sort(key=lambda c: (not any(h in str(c).lower() for h in _TEAM_HINTS), str(c)))
    return cols


@guard
def page_teams():
    page_header("Care Teams")
    if C.f.empty:
        st.info("No events to show.")
        return

    if C.staff:
        w = C.f.groupby([C.dept, C.staff]).size().reset_index(name="Event records")
        table(w.sort_values("Event records", ascending=False))
        top = w.nlargest(30, "Event records")
        chart(lambda: px.bar(top, x=C.staff, y="Event records", color=C.dept, barmode="group"))
        st.caption("Showing the 30 busiest staff/department combinations. Verify the staff mapping before relying on it.")
        return

    st.caption("This event log has no staff or resource column, so teams are shown by care unit and service "
               "fields instead. These describe where and for whom work happened, not individual staff. "
               "Map a real staff column under **Field mapping** to see per-staff workload.")
    cols = _team_columns()
    if not cols:
        st.info("No suitable grouping fields were found. Fields available: " + ", ".join(map(str, C.raw.columns)))
        return

    col = st.selectbox("Group workload by", cols, key="teams_group",
                       format_func=lambda c: str(c).replace("_", " ").capitalize()
                       + (" (demo labels)" if C.synthetic and c == C.dept else ""))
    d = C.f.assign(_grp=C.f[col].fillna("Unknown").astype(str))
    agg = {"Events": ("_grp", "size")}
    if C.case:
        agg["Cases"] = (C.case, "nunique")
    summary = d.groupby("_grp").agg(**agg).reset_index().rename(columns={"_grp": str(col)})
    summary["Share of events (%)"] = (summary["Events"] / summary["Events"].sum() * 100).round(1)
    summary = summary.sort_values("Events", ascending=False)

    kpis([("Groups", f"{len(summary):,}"),
          ("Events", f"{int(summary['Events'].sum()):,}"),
          ("Busiest group", str(summary.iloc[0][str(col)])[:28]),
          ("Busiest share", f"{summary.iloc[0]['Share of events (%)']:.1f}%")])
    st.write("")

    n = pick_top(len(summary), "Groups to chart", "teams_n", default=15, cap=40)
    top = summary.head(n)

    def bar():
        fig = px.bar(top, x="Events", y=str(col), orientation="h",
                     hover_data=[c for c in ("Cases", "Share of events (%)") if c in top.columns])
        fig.update_traces(marker_color=PALETTE[0])
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=120 + 30 * len(top))
        return fig
    chart(bar)

    if C.act:
        st.markdown("**Activity mix by group**")
        keep = summary.head(12)[str(col)].tolist()
        m = (d[d["_grp"].isin(keep)].assign(_act=lambda x: x[C.act].fillna("Unknown activity").astype(str))
             .pivot_table(index="_grp", columns="_act", values=C.act, aggfunc="size", fill_value=0))
        chart(lambda: None if m.empty else px.imshow(
            m, aspect="auto", text_auto=True, labels=dict(x="Activity", y=str(col), color="Events"))
            .update_layout(height=140 + 32 * len(m)), "Not enough data for this view.")
        st.caption("Shows the 12 busiest groups. Darker cells mean more recorded events of that activity.")

    table(summary.head(200))
    st.download_button("Export team workload CSV", summary.to_csv(index=False).encode("utf-8"),
                       "careflow_team_workload.csv", "text/csv", key="teams_dl")


@guard
def page_reports():
    page_header("Reports & Outcomes")
    st.write("Generate an overview from the loaded event log.")
    a, b, c = st.columns(3)
    a.metric("Event records", f"{len(C.f):,}")
    b.metric("Cases / patients", f"{C.n_cases:,}")
    c.metric("Activities", f"{C.f[C.act].nunique():,}" if C.act else "Not detected")
    if C.case and C.time:
        dur = cached_durations(C.f, C.case, C.time)
        if not dur.empty:
            o1, o2 = st.columns(2)
            o1.metric("Cases with usable timestamps", f"{len(dur):,}")
            o2.metric("Median observed elapsed time", fmt_hours(dur["Elapsed hours"].median()))
            st.caption("Elapsed time is the span between first and last recorded event, not necessarily length of stay.")
    summary = C.f.describe(include="all").transpose().astype(str).reset_index(names="Field")
    table(summary)
    st.download_button("Download filtered event log CSV", C.f.to_csv(index=False).encode("utf-8"),
                       "careflow_filtered_event_log.csv", "text/csv")


@guard
def page_quality():
    page_header("Data Quality Studio")
    st.caption("Review missing fields, duplicates, timestamp quality and event-log readiness before interpreting analytics.")
    f = C.f
    q = st.columns(4)
    q[0].metric("Rows", f"{len(f):,}")
    q[1].metric("Columns", f"{len(f.columns):,}")
    q[2].metric("Duplicate rows", f"{int(f.duplicated().sum()):,}")
    q[3].metric("Rows with missing values", f"{int(f.isna().any(axis=1).sum()):,}")
    roles = {C.case: "Case ID", C.act: "Activity", C.time: "Timestamp", C.dept: "Department",
             C.status: "Status", C.staff: "Staff/resource"}
    rep = pd.DataFrame({
        "Field": f.columns.astype(str),
        "Detected role": [roles.get(c, "Other") for c in f.columns],
        "Missing values": [int(f[c].isna().sum()) for c in f.columns],
        "Missing %": [round(float(f[c].isna().mean() * 100), 2) for c in f.columns],
        "Unique values": [int(f[c].nunique(dropna=True)) for c in f.columns],
    })
    table(rep)
    if C.time:
        raw_t = C.raw[C.time]
        t1, t2 = st.columns(2)
        t1.metric("Missing / unparseable timestamps", f"{int(raw_t.isna().sum()):,}")
        t2.metric("Timestamp parse success", f"{100 * raw_t.notna().mean():.1f}%" if len(raw_t) else "N/A")
    else:
        st.warning("No timestamp column mapped. Time-based ordering and elapsed-time analysis are unavailable.")
    if C.case and C.act:
        st.caption("Process-mining readiness: case and activity columns are mapped. Confirm that case IDs are "
                   "pseudonymised and events are correctly ordered before operational use.")
    st.download_button("Download data-quality report", rep.to_csv(index=False).encode("utf-8"),
                       "careflow_data_quality_report.csv", "text/csv")


@guard
def page_dictionary():
    page_header("Data Dictionary")
    st.caption("Columns in the loaded event log and the process-mining role each was mapped to.")
    role_names = {C.case: "Case / encounter identifier", C.act: "Activity / event", C.time: "Timestamp",
                  C.status: "Status / outcome", C.staff: "Staff / resource",
                  C.dept: "Synthetic demo department (not source data)" if C.synthetic else "Department / unit"}
    d = pd.DataFrame([{
        "Source field": str(c), "Detected role": role_names.get(c, "Unmapped"), "Data type": str(C.raw[c].dtype),
        "Example value": str(C.raw[c].dropna().iloc[0])[:120] if C.raw[c].notna().any() else "(all values missing)",
    } for c in C.raw.columns])
    table(d)
    st.download_button("Export data dictionary", d.to_csv(index=False).encode("utf-8"), "careflow_data_dictionary.csv", "text/csv")
    st.info("Role detection is based on column names. Review or override it under Field mapping in the sidebar.")


@guard
def page_insights():
    page_header("Insights & Benchmarks")
    st.caption("Descriptive insights from the loaded event log, not external hospital benchmarks or clinical recommendations.")
    f = C.f
    a, b, c = st.columns(3)
    a.metric("Records in view", f"{len(f):,}")
    b.metric("Distinct cases", f"{C.n_cases:,}" if C.case else "Not detected")
    c.metric("Missing-value cells", f"{int(f.isna().sum().sum()):,}")
    l, r = st.columns(2)
    with l:
        st.markdown("#### Data completeness by field")
        comp = pd.DataFrame({"Field": f.columns.astype(str),
                             "Completeness (%)": [round(float(f[c].notna().mean() * 100), 1) for c in f.columns]})
        chart(lambda: px.bar(comp.sort_values("Completeness (%)").head(18), x="Completeness (%)", y="Field",
                             orientation="h", range_x=[0, 100], color="Completeness (%)"))
    with r:
        st.markdown("#### Event volume by activity")
        chart(lambda: fig_bar_counts(C.act, "Activity", 12, height=420), "No activity column is mapped.")
    if C.case:
        st.markdown("#### Events per case")
        per_case = f.groupby(C.case).size().rename("Events per case").reset_index()
        chart(lambda: px.histogram(per_case, x="Events per case", nbins=25).update_traces(marker_color=PALETTE[0]))
        table(per_case["Events per case"].describe().round(2).rename_axis("Statistic").reset_index())
    st.info("Validate definitions and clinical context with qualified staff before operational use.")


@guard
def page_governance():
    page_header("Security & Governance")
    f = C.f
    a, b, c = st.columns(3)
    a.metric("Rows", f"{len(f):,}")
    b.metric("Columns", f"{len(f.columns):,}")
    c.metric("Rows with any missing data", f"{int(f.isna().any(axis=1).sum()):,}")
    for label, col in [("case identifier", C.case), ("activity", C.act), ("timestamp", C.time)]:
        (st.info if col else st.warning)(
            f"Detected {label} field: {col}" if col else f"No {label} column mapped. Use Field mapping in the sidebar.")
    st.markdown("#### Data-handling checklist")
    st.markdown(
        "- Use pseudonymised case IDs; avoid names, MRNs and free-text clinical notes in the event log.\n"
        "- Do not commit identifiable patient data or secrets to a public repository.\n"
        "- Uploaded files stay in this browser session only.\n"
        "- Tasks, profiles and reminders are session-only until backed by a protected, audited database."
    )


@guard
def page_tasks():
    page_header("Task & Escalation Center", chips=False)
    st.caption("Track follow-up work in this active session. Tasks are not yet saved to a shared database or hospital system.")
    if "careflow_tasks" not in st.session_state:
        st.session_state.careflow_tasks = [
            {"Task":"Review pathway deviation", "Owner":"Pathway Lead", "Priority":"High", "Status":"Open", "Due date":"Not set"},
            {"Task":"Validate event-log timestamps", "Owner":"Data Quality Team", "Priority":"Medium", "Status":"In progress", "Due date":"Not set"},
        ]
    with st.form("careflow_add_task_form", clear_on_submit=True):
        st.markdown("#### Create a task")
        c1, c2 = st.columns(2)
        with c1:
            task_title = st.text_input("Task title")
            task_owner = st.text_input("Assigned owner / team")
            task_due = st.date_input("Due date")
        with c2:
            task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            task_status = st.selectbox("Status", ["Open", "In progress", "Blocked", "Done"])
        add_task = st.form_submit_button("Add task", use_container_width=True)
    if add_task:
        if task_title.strip():
            st.session_state.careflow_tasks.append({"Task":task_title.strip(), "Owner":task_owner.strip() or "Unassigned", "Priority":task_priority, "Status":task_status, "Due date":str(task_due)})
            st.success("Task added for this session.")
        else:
            st.error("Enter a task title first.")
    tasks_df = pd.DataFrame(st.session_state.careflow_tasks)
    if not tasks_df.empty:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total tasks", len(tasks_df))
        m2.metric("Open", int((tasks_df["Status"] == "Open").sum()))
        m3.metric("In progress", int((tasks_df["Status"] == "In progress").sum()))
        m4.metric("High priority", int((tasks_df["Priority"] == "High").sum()))
        st.dataframe(tasks_df, use_container_width=True, hide_index=True)
        st.download_button("Export tasks CSV", tasks_df.to_csv(index=False).encode("utf-8"), "careflow_tasks.csv", "text/csv")
    st.warning("For real hospital use, connect tasks to a protected database with role-based permissions and an audit trail before relying on them operationally.")


@guard
def page_notifications():
    page_header("Notifications Center", chips=False)
    st.caption("Session-level reminders and app notices. These are not connected to a live hospital alerting system.")
    if "careflow_notifications" not in st.session_state:
        st.session_state.careflow_notifications = [
            {"Type": "Data quality", "Title": "Review event-log quality", "Details": "Check missing fields and timestamp parsing in Data Quality Studio.", "Status": "Unread"},
            {"Type": "Security", "Title": "Protect sensitive information", "Details": "Avoid committing identifiable patient data or secrets to a public repository.", "Status": "Unread"},
        ]
    with st.form("careflow_add_notification_form", clear_on_submit=True):
        n1, n2 = st.columns(2)
        with n1:
            notification_title = st.text_input("Reminder title")
            notification_type = st.selectbox("Category", ["General", "Data quality", "Security", "Reporting", "Task follow-up"])
        with n2:
            notification_details = st.text_area("Reminder details")
            notification_status = st.selectbox("Initial status", ["Unread", "Read"])
        add_notification = st.form_submit_button("Add reminder", use_container_width=True)
    if add_notification:
        if notification_title.strip():
            st.session_state.careflow_notifications.insert(0, {"Type": notification_type, "Title": notification_title.strip(), "Details": notification_details.strip(), "Status": notification_status})
            st.success("Reminder added for this session.")
        else:
            st.error("Enter a reminder title.")
    notices_df = pd.DataFrame(st.session_state.careflow_notifications)
    if not notices_df.empty:
        unread = int((notices_df["Status"] == "Unread").sum())
        st.metric("Unread reminders", unread)
        st.dataframe(notices_df, use_container_width=True, hide_index=True)
        if st.button("Mark all reminders as read", use_container_width=True):
            for notice in st.session_state.careflow_notifications:
                notice["Status"] = "Read"
            st.rerun()
        st.download_button("Export reminders", notices_df.to_csv(index=False).encode("utf-8"), "careflow_reminders.csv", "text/csv")
    st.warning("Reminders are session-only. They are not sent as email, SMS, push notifications, or clinical alerts.")


@guard
def page_saved():
    page_header("Saved Workspace", chips=False)
    st.caption("Save a named snapshot of the current dataset and filters. Saved views are temporary and session-only.")
    if "careflow_saved_views" not in st.session_state:
        st.session_state.careflow_saved_views = []
    with st.form("careflow_saved_workspace_form", clear_on_submit=True):
        view_name = st.text_input("Workspace name", placeholder="e.g. Monthly pathway review")
        view_notes = st.text_area("Notes", placeholder="What are you reviewing?")
        save_view = st.form_submit_button("Save current workspace", use_container_width=True)
    if save_view:
        if view_name.strip():
            st.session_state.careflow_saved_views.insert(0, {"Name":view_name.strip(),"Page":st.session_state.get("careflow_page", ""),"Data source":C.source,"Rows in current view":int(len(C.f)),"Department filter":str(C.dept_summary),"Active filters":C.active or "None","Notes":view_notes.strip()})
            st.success("Workspace saved for this session.")
        else:
            st.error("Enter a workspace name first.")
    if st.session_state.careflow_saved_views:
        views_df = pd.DataFrame(st.session_state.careflow_saved_views)
        st.dataframe(views_df, use_container_width=True, hide_index=True)
        st.download_button("Export saved workspaces", views_df.to_csv(index=False).encode("utf-8"), "careflow_saved_workspaces.csv", "text/csv")
        if st.button("Clear saved workspaces"):
            st.session_state.careflow_saved_views = []
            st.rerun()
    else:
        st.markdown('<div class="cf-feature-card"><div class="cf-feature-title">Your analysis workspace, organized</div><div class="cf-feature-copy">Save a named snapshot of the dataset and filters you are reviewing. For now, saved views exist only during the current session.</div></div>', unsafe_allow_html=True)


@guard
def page_prefs():
    page_header("Display Preferences", chips=False)
    st.caption("Personalize your review experience. Settings apply only to the active session.")
    if "careflow_display_preferences" not in st.session_state:
        st.session_state.careflow_display_preferences = {"density":"Comfortable","chart_labels":True,"compact_tables":False}
    prefs = st.session_state.careflow_display_preferences
    with st.form("careflow_display_preferences_form"):
        density = st.radio("Layout density", ["Comfortable","Compact"], horizontal=True, index=0 if prefs["density"] == "Comfortable" else 1)
        chart_labels = st.checkbox("Show chart labels where supported", value=prefs["chart_labels"])
        compact_tables = st.checkbox("Prefer compact table views", value=prefs["compact_tables"])
        save_prefs = st.form_submit_button("Save preferences", use_container_width=True)
    if save_prefs:
        st.session_state.careflow_display_preferences = {"density":density,"chart_labels":chart_labels,"compact_tables":compact_tables}
        st.success("Preferences saved for this session.")
    p1,p2,p3 = st.columns(3)
    p1.markdown('<div class="cf-feature-card"><div class="cf-feature-title">Comfortable reading</div><div class="cf-feature-copy">Balanced spacing for longer review sessions.</div></div>', unsafe_allow_html=True)
    p2.markdown('<div class="cf-feature-card"><div class="cf-feature-title">Clear visual hierarchy</div><div class="cf-feature-copy">Consistent headings, cards, and chart containers.</div></div>', unsafe_allow_html=True)
    p3.markdown('<div class="cf-feature-card"><div class="cf-feature-title">Responsive workspace</div><div class="cf-feature-copy">Designed for desktop and smaller screens.</div></div>', unsafe_allow_html=True)
    st.info("Persistent preferences require secure user-specific storage.")


@guard
def page_help():
    page_header("Help Center", chips=False)
    st.caption("Guidance for using the analytics workspace and troubleshooting common issues.")
    q1,q2,q3 = st.columns(3)
    q1.metric("Help topics", "6")
    q2.metric("Support channel", "Form")
    q3.metric("Service status", "App session")
    with st.expander("How do I load my actual event log?", expanded=True):
        st.write("Place the approved CSV file beside app.py in the repository using one of the configured filenames: careflow_event_log.csv, event_log_ED_MMA_2026.csv, or sample_event_log.csv. Do not commit identifiable patient data to a public repository. You can also upload a CSV under Data source in the sidebar (kept in this browser session only), and place process-mining output CSVs in a pm_outputs/ folder.")
    with st.expander("Why are department names marked as synthetic?"):
        st.write("If the source event log has no department field, CareFlow creates demo labels for visualization. These are not real department assignments and should not be used for operational decisions.")
    with st.expander("Why is a chart or metric missing?"):
        st.write("CareFlow detects columns by name. Ensure your event log includes appropriate case/encounter ID, activity/event, and timestamp columns. Rename source columns clearly if detection fails.")
    with st.expander("How do I troubleshoot login problems?"):
        st.write("Confirm SUPABASE_URL and SUPABASE_KEY are correctly configured in Streamlit Cloud Secrets, and check whether email verification is enabled in Supabase. Never share passwords or secret keys in support requests.")
    with st.expander("Are tasks, profiles, and support requests permanently saved?"):
        st.write("Not by this version of the app. Some entries are stored only in the active Streamlit session. Configure secure database tables, access controls, retention, and audit logging before using them as persistent hospital records.")
    with st.expander("Can CareFlow provide clinical recommendations?"):
        st.write("No. Current features summarize observed event-log patterns. They are not a diagnostic, triage, or treatment recommendation system.")
    st.markdown("#### Contact support")
    with st.form("careflow_support_form", clear_on_submit=True):
        support_topic = st.selectbox("Topic", ["Login / account", "Data loading", "Charts / reports", "Task management", "Security / privacy", "Other"])
        support_email = st.text_input("Reply email (optional)", value=st.session_state.careflow_user.get("email", ""))
        support_message = st.text_area("Describe the issue (do not include patient-identifying information)")
        send_support = st.form_submit_button("Submit support request", use_container_width=True)
    if send_support:
        if support_message.strip():
            if "careflow_support_requests" not in st.session_state:
                st.session_state.careflow_support_requests = []
            st.session_state.careflow_support_requests.append({"Topic":support_topic, "Email":support_email.strip(), "Message":support_message.strip()})
            st.success("Support request captured for this session. It has not been emailed or sent to a support team.")
        else:
            st.error("Please describe the issue before submitting.")


@guard
def page_profile():
    page_header("Profile", chips=False)
    st.caption("Choose the profile that matches how you use CareFlow. Profile details are currently saved only for this browser session.")

    user = st.session_state.careflow_user
    email = user.get("email", "")
    profile_type = st.radio(
        "Profile type",
        ["Client / Patient", "Doctor / Clinician"],
        horizontal=True,
        key="careflow_profile_type",
        help="This selects the profile form only; it does not grant or restrict system permissions.",
    )

    if profile_type == "Client / Patient":
        st.markdown("### 👤 Client profile")
        st.info("Only enter information needed for your account. Do not enter medical record numbers or sensitive clinical details in this demo profile.")
        with st.form("client_profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                client_name = st.text_input("Full name")
                client_age = st.number_input("Age", min_value=0, max_value=120, value=18)
                client_gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Other"])
            with c2:
                client_phone = st.text_input("Contact number (optional)")
                client_city = st.text_input("City / Location (optional)")
                client_preferred_contact = st.selectbox("Preferred contact method", ["Email", "Phone", "No preference"])
            st.text_input("Account email", value=email, disabled=True)
            client_notes = st.text_area("Accessibility or communication preference (optional)", placeholder="Avoid sharing diagnosis, patient IDs, or other sensitive health details.")
            client_submitted = st.form_submit_button("Save client profile", use_container_width=True)
        if client_submitted:
            st.session_state["careflow_client_profile"] = {
                "Name": client_name.strip(), "Age": client_age, "Gender": client_gender,
                "Contact number": client_phone.strip(), "City": client_city.strip(),
                "Preferred contact": client_preferred_contact, "Email": email,
                "Communication preference": client_notes.strip(),
            }
            st.success("Client profile saved for this session.")
            st.warning("This profile is not permanently stored or shared with a care team. Do not use it as a clinical record.")
        saved_client = st.session_state.get("careflow_client_profile")
        if saved_client:
            with st.expander("View saved client profile"):
                st.json(saved_client)

    else:
        st.markdown("### 🩺 Doctor / clinician profile")
        with st.form("doctor_profile_form"):
            st.markdown("#### Personal information")
            col1, col2 = st.columns(2)
            with col1:
                doctor_name = st.text_input("Doctor / clinician name")
                doctor_gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Other"])
                doctor_phone = st.text_input("Contact number")
            with col2:
                doctor_department = st.selectbox("Department", ["Emergency", "General Medicine", "Cardiology", "Neurology", "Paediatrics", "Orthopaedics", "Surgery", "Radiology", "Other"])
                doctor_designation = st.selectbox("Designation", ["Doctor", "Resident Doctor", "Consultant", "Senior Consultant", "Department Head", "Nurse", "Care Coordinator", "Analyst", "Other"])
                doctor_hospital = st.text_input("Hospital / healthcare facility")
            st.text_input("Account email", value=email, disabled=True)
            st.markdown("#### Professional information")
            col3, col4 = st.columns(2)
            with col3:
                doctor_qualification = st.text_input("Qualification")
                doctor_specialization = st.text_input("Specialization")
            with col4:
                doctor_experience = st.number_input("Years of experience", min_value=0, max_value=70, value=0)
                doctor_location = st.text_input("City / Location")
            doctor_bio = st.text_area("Professional bio (optional)")
            doctor_submitted = st.form_submit_button("Save clinician profile", use_container_width=True)
        if doctor_submitted:
            st.session_state["careflow_doctor_profile"] = {
                "Name": doctor_name.strip(), "Gender": doctor_gender, "Contact number": doctor_phone.strip(),
                "Department": doctor_department, "Designation": doctor_designation,
                "Hospital": doctor_hospital.strip(), "Email": email,
                "Qualification": doctor_qualification.strip(), "Specialization": doctor_specialization.strip(),
                "Experience years": doctor_experience, "Location": doctor_location.strip(), "Bio": doctor_bio.strip(),
            }
            st.success("Clinician profile saved for this session.")
            st.warning("This is a profile form, not professional credential verification. Details are not permanently stored yet.")
        saved_doctor = st.session_state.get("careflow_doctor_profile")
        if saved_doctor:
            with st.expander("View saved clinician profile"):
                st.json(saved_doctor)


# ======================================================================
# PROCESS DISCOVERY & METRICS  (reads the files written by pipeline/*.py)
# ======================================================================
_APP_DIR = Path(__file__).resolve().parent
PM_DIRS = [Path("pm_outputs"), Path("process_mining_outputs"), Path("."),
           _APP_DIR / "pm_outputs", _APP_DIR]


def _pm_find(name):
    """Locate an output file in pm_outputs/, the repo root, or beside app.py."""
    for d in PM_DIRS:
        p = d / name
        if p.is_file():
            return p
    return None


@st.cache_data(show_spinner=False)
def _pm_file(path, mtime):
    return pd.read_csv(path)


def _pm_read(name):
    """Return a DataFrame for the named output file, or None if missing/unreadable."""
    p = _pm_find(name)
    if p is None:
        return None
    try:
        return _pm_file(str(p), p.stat().st_mtime)
    except Exception:  # noqa: BLE001
        return None


def _fmt_minutes(m):
    if m is None or pd.isna(m):
        return "—"
    return f"{m / 60:,.1f} h" if m >= 120 else f"{m:,.0f} min"


@guard
def page_discovery():
    page_header("Process Discovery & Metrics",
                "Process model and metrics produced by the offline process-mining pipeline.", chips=False)
    st.caption("Observed workflow from recorded events. This describes what happened; it does not recommend "
               "clinical treatment. These results come from files in pm_outputs/, not from the sidebar filters.")

    pathways = _pm_read("pathway_frequencies.csv")
    trans = _pm_read("transition_metrics.csv")
    cases = _pm_read("case_metrics.csv")
    model_png = _pm_find("careflow_process_map.png")

    if pathways is None and trans is None and cases is None and model_png is None:
        st.info("No pipeline outputs found. Run `python pipeline/calculate_metrics.py --input <event_log.csv>` and "
                "`python pipeline/discover_process.py --input <event_log.csv>`, then place the results in a "
                "`pm_outputs/` folder beside app.py.")
        return

    if cases is not None:
        dur = cases["observed_duration_minutes"]
        kpis([
            ("Cases", f"{len(cases):,}"),
            ("Distinct pathways", f"{len(pathways):,}" if pathways is not None else "—"),
            ("Distinct transitions", f"{len(trans):,}" if trans is not None else "—"),
            ("Median case duration", _fmt_minutes(dur.median())),
            ("90th percentile", _fmt_minutes(dur.quantile(0.9))),
        ])
        st.write("")

    tab_model, tab_paths, tab_trans, tab_cases = st.tabs(
        ["Process model", "Pathway frequencies", "Transition metrics", "Case durations"])

    with tab_model:
        if model_png is not None:
            st.image(str(model_png), caption="Petri net discovered with the Inductive Miner (PM4Py). "
                     "Black boxes are silent transitions that allow a step to be skipped or the flow to split/join.",
                     **WIDE)
            st.download_button("Download process map (PNG)", model_png.read_bytes(),
                               "careflow_process_map.png", "image/png")
            st.caption("The Inductive Miner favours a model that replays every recorded case. As a result the "
                       "model is permissive: it allows many activity orders that rarely or never occur. Use the "
                       "Pathway frequencies tab to see which sequences actually dominate.")
        else:
            st.info("careflow_process_map.png was not found in pm_outputs/.")

    with tab_paths:
        if pathways is None:
            st.info("pathway_frequencies.csv was not found in pm_outputs/.")
        else:
            top10 = pathways.head(10)["case_percent"].sum()
            a, b = st.columns(2)
            a.metric("Most common pathway", f"{pathways.iloc[0]['case_percent']:.1f}% of cases")
            b.metric("Top 10 pathways cover", f"{top10:.1f}% of cases")
            q = st.text_input("Search pathways by activity name", key="disc_path_q")
            shown = pathways
            if q.strip():
                shown = pathways[pathways["pathway"].str.contains(q.strip(), case=False, regex=False)]
            if shown.empty:
                st.info("No pathway contains that text.")
            else:
                n = pick_top(len(shown), "Pathways to chart", "disc_path_n", default=10)
                top = shown.head(n).copy()
                top["Variant"] = [f"V{i}" for i in top.index + 1]

                def bar():
                    fig = px.bar(top, x="case_count", y="Variant", orientation="h",
                                 hover_data=["pathway", "case_percent"],
                                 labels={"case_count": "Cases", "case_percent": "% of cases"})
                    fig.update_traces(marker_color=PALETTE[0])
                    fig.update_layout(yaxis={"autorange": "reversed"}, height=120 + 30 * len(top))
                    return fig
                chart(bar)
                table(shown.rename(columns={"pathway": "Observed pathway", "case_count": "Cases",
                                            "case_percent": "Share of cases (%)"}).head(200))
                st.download_button("Export pathways CSV", shown.to_csv(index=False).encode("utf-8"),
                                   "careflow_pathway_frequencies.csv", "text/csv", key="disc_path_dl")

    with tab_trans:
        if trans is None:
            st.info("transition_metrics.csv was not found in pm_outputs/.")
        else:
            min_n = st.slider("Minimum transitions to include", 1, int(max(trans["transition_count"].max(), 2)),
                              1, key="disc_trans_min")
            t = trans[trans["transition_count"] >= min_n].copy()
            t["Step"] = t["from_activity"] + " → " + t["to_activity"]

            def waits():
                w = t.dropna(subset=["median_minutes"]).nlargest(15, "median_minutes")
                if w.empty:
                    return None
                fig = px.bar(w, x="median_minutes", y="Step", orientation="h",
                             hover_data=["transition_count", "average_minutes"],
                             labels={"median_minutes": "Median wait (min)"})
                fig.update_traces(marker_color=PALETTE[1])
                fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=140 + 28 * len(w))
                return fig
            st.markdown("**Longest median gaps between consecutive events**")
            chart(waits, "No transitions meet the minimum count.")
            st.caption("Long gaps can reflect documentation delays as well as real queues. "
                       "Negative time intervals are excluded from time statistics.")
            table(t.drop(columns=["Step"]).rename(columns={
                "from_activity": "From", "to_activity": "To", "transition_count": "Transitions",
                "valid_time_count": "Valid timings", "average_minutes": "Avg (min)", "median_minutes": "Median (min)"}))
            st.download_button("Export transitions CSV", t.drop(columns=["Step"]).to_csv(index=False).encode("utf-8"),
                               "careflow_transition_metrics.csv", "text/csv", key="disc_trans_dl")

    with tab_cases:
        if cases is None:
            st.info("case_metrics.csv was not found in pm_outputs/.")
        else:
            dur_h = (cases["observed_duration_minutes"] / 60).rename("Observed duration (h)")
            cap = float(dur_h.quantile(0.99))
            chart(lambda: px.histogram(dur_h[dur_h <= cap].to_frame(), x="Observed duration (h)", nbins=40)
                  .update_traces(marker_color=PALETTE[0]).update_layout(height=320))
            st.caption(f"Duration is first to last recorded event. Chart trimmed at the 99th percentile "
                       f"({cap:,.1f} h) so a few very long cases do not flatten it.")
            ev = cases["event_count"].value_counts().sort_index().rename_axis("Events per case") \
                .reset_index(name="Cases")
            chart(lambda: px.bar(ev, x="Events per case", y="Cases").update_traces(marker_color=PALETTE[1])
                  .update_layout(height=280, xaxis=dict(dtick=1)))
            st.caption("Individual case IDs are intentionally not listed on this page.")
    source_note("pm_outputs/ (generated by pipeline/calculate_metrics.py and pipeline/discover_process.py)")



# ======================================================================
# NAVIGATION (requires Streamlit >= 1.37 for st.navigation + Material icons)
# ======================================================================
def _page(fn, title, icon, slug, default=False):
    return st.Page(fn, title=title, icon=f":material/{icon}:", url_path=None if default else slug, default=default)


NAV = {
    "Analytics": [
        _page(page_dashboard, "Executive Dashboard", "dashboard", "dashboard", default=True),
        _page(page_pm_explorer, "Process Mining Explorer", "account_tree", "process-mining"),
        _page(page_patient_flow, "Patient Flow", "timeline", "patient-flow"),
        _page(page_pathways, "Clinical Pathways", "route", "clinical-pathways"),
        _page(page_comparison, "Pathway Comparison", "compare_arrows", "pathway-comparison"),
        _page(page_discovery, "Process Discovery & Metrics", "schema", "process-discovery"),
    ],
    "Operations": [
        _page(page_beds, "Bed & Discharge Management", "bed", "beds-discharge"),
        _page(page_tasks, "Task & Escalation Center", "task_alt", "tasks"),
        _page(page_coordination, "Care coordination", "hub", "care-coordination"),
        _page(page_teams, "Care Teams", "groups", "care-teams"),
        _page(page_notifications, "Notifications Center", "notifications", "notifications"),
    ],
    "Data & Governance": [
        _page(page_reports, "Reports & Outcomes", "summarize", "reports"),
        _page(page_quality, "Data Quality Studio", "fact_check", "data-quality"),
        _page(page_dictionary, "Data Dictionary", "menu_book", "data-dictionary"),
        _page(page_insights, "Insights & Benchmarks", "insights", "insights"),
        _page(page_governance, "Security & Governance", "shield", "governance"),
    ],
    "Workspace": [
        _page(page_saved, "Saved Workspace", "bookmark", "saved-workspace"),
        _page(page_prefs, "Display Preferences", "tune", "preferences"),
        _page(page_help, "Help Center", "help", "help"),
        _page(page_profile, "Profile", "person", "profile"),
    ],
}
# Pages that work without an event log (session-only forms and help).
SESSION_PAGES = {"Process Discovery & Metrics", "Task & Escalation Center", "Notifications Center", "Saved Workspace",
                 "Display Preferences", "Help Center", "Profile"}

pg = st.navigation(NAV)
st.session_state["careflow_page"] = pg.title


def render_account():
    with st.sidebar:
        st.divider()
        st.caption("Signed in as: " + str(st.session_state.careflow_user["email"]))
        if st.button("Log out", key="cf_logout", **WIDE):
            try:
                supabase.auth.sign_out()
            except Exception:  # noqa: BLE001
                pass
            st.session_state.careflow_user = None
            st.rerun()


# ======================================================================
# LOAD DATA -> MAP FIELDS -> FILTER -> CONTEXT
# ======================================================================
data_box = st.sidebar.expander("Data source", expanded=False)
with data_box:
    uploaded = st.file_uploader("Upload event log (CSV)", type="csv", key="cf_upload",
                                help="Replaces the repository file for this browser session only.")
    st.caption("Uploads are not stored. Avoid identifiable patient data on a public deployment.")

with st.spinner("Loading event log…"):
    raw, source_name, load_error = load_event_log(uploaded)
    pm_outputs, pm_notes = discover_pm_outputs()

with data_box:
    st.caption(f"Active file: **{source_name}**")
    if pm_outputs:
        st.caption("Process-mining outputs found: " + ", ".join(f"{k} ({v['file']})" for k, v in pm_outputs.items()))
    else:
        st.caption("No process-mining output files found (looked in pm_outputs/). Results are computed live.")
    for note in pm_notes:
        st.warning(note)

block = None  # (severity, message) when data pages cannot render
if raw.empty:
    C = Ctx(raw=pd.DataFrame(), f=pd.DataFrame(), source=source_name, case=None, act=None, time=None, dept=None,
            status=None, staff=None, synthetic=False, pm_outputs={}, dept_summary="—")
    block = ("error", load_error or "No event-log CSV was found.")
else:
    auto = pm.detect_roles(raw)
    LABELS = {"case": "Case / patient ID", "activity": "Activity", "time": "Timestamp",
              "dept": "Department", "status": "Status", "staff": "Staff / resource"}
    opts = [None] + list(raw.columns)
    chosen = {}
    with st.sidebar.expander("Field mapping", expanded=False):
        st.caption("Auto-detected from column names. Override anything that was missed or wrong.")
        for role, label in LABELS.items():
            chosen[role] = st.selectbox(label, opts, index=opts.index(auto[role]) if auto[role] in opts else 0,
                                        key=f"map_{role}_{source_name}",
                                        format_func=lambda c: "(none)" if c is None else str(c))
        picked = [c for c in chosen.values() if c is not None]
        if len(set(picked)) != len(picked):
            st.warning("Each column should be used for only one role.")

    df, dept_col, synthetic = prepare_log(raw, chosen["case"], chosen["time"], chosen["dept"])
    case_c, act_c, time_c = chosen["case"], chosen["activity"], chosen["time"]

    # ---- global filters (apply to every analytics page) ----
    fkeys = {n: f"flt_{n}_{source_name}" for n in ("depts", "acts", "dates", "whole")}

    def reset_filters():
        for k in fkeys.values():
            st.session_state.pop(k, None)

    sel_depts, sel_acts, whole, date_range = [], [], True, None
    with st.sidebar:
        st.markdown("### Filters")
        sel_depts = st.multiselect(
            "Department (demo labels)" if synthetic else "Department",
            sorted(df[dept_col].dropna().astype(str).unique()), key=fkeys["depts"], placeholder="All departments")
        if act_c:
            sel_acts = st.multiselect(
                "Activity", sorted(df[act_c].fillna("Unknown activity").astype(str).unique()),
                key=fkeys["acts"], placeholder="All activities")
            if sel_acts and case_c:
                whole = st.checkbox("Keep whole cases that include these activities", value=True, key=fkeys["whole"])
        if time_c and df[time_c].notna().any():
            lo, hi = df[time_c].min().date(), df[time_c].max().date()
            date_range = st.date_input("Event dates", value=(lo, hi), min_value=lo, max_value=hi, key=fkeys["dates"])
            date_range = tuple(date_range) if isinstance(date_range, (tuple, list)) else None
        st.button("Reset filters", on_click=reset_filters, key="cf_reset_filters", **WIDE)

    f = pm.apply_filters(df, case=case_c, act=act_c, time=time_c, dept=dept_col, depts=sel_depts, acts=sel_acts,
                         date_range=date_range, keep_whole_cases=whole)
    active = []
    if sel_depts:
        active.append("department")
    if sel_acts:
        active.append(f"{len(sel_acts)} activit{'y' if len(sel_acts) == 1 else 'ies'}")
    if date_range and len(date_range) == 2 and time_c:
        full = df[time_c].dropna()
        if not full.empty and (pd.Timestamp(date_range[0]) > full.min().normalize()
                               or pd.Timestamp(date_range[1]) < full.max().normalize()):
            active.append("dates")

    C = Ctx(raw=df, f=f, source=source_name, case=case_c, act=act_c, time=time_c, dept=dept_col,
            status=chosen["status"], staff=chosen["staff"], synthetic=synthetic, pm_outputs=pm_outputs,
            dept_summary=", ".join(sel_depts) or "All departments", active=", ".join(active))
    if f.empty:
        block = ("warning", "No events match the current filters. Widen the selection or press **Reset filters** in the sidebar.")

render_account()

# ======================================================================
# RENDER
# ======================================================================
if block and pg.title not in SESSION_PAGES:
    page_header(pg.title, chips=False)
    (st.error if block[0] == "error" else st.warning)(block[1])
    if block[0] == "error":
        st.markdown(
            "**To get started**\n\n"
            "- Upload a CSV under **Data source** in the sidebar, or\n"
            "- Place `careflow_event_log.csv`, `event_log_ED_MMA_2026.csv` or `sample_event_log.csv` beside `app.py`.\n\n"
            "The file needs a case/patient ID, an activity and (ideally) a timestamp column."
        )
    footer()
else:
    pg.run()
