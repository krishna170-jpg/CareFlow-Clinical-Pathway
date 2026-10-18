import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

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
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 78% 20%, #d9f3ff 0, transparent 34%),
                        linear-gradient(120deg, #f7fcff 0%, #e7f7ff 48%, #cceeff 100%);
        }
        [data-testid="stHeader"] { background: transparent; }
        .block-container { padding-top: 1.5rem; padding-bottom: 1.4rem; max-width: 1500px; }
        .cf-login-brand { color:#0b3970; font-size:clamp(38px,4.2vw,66px); font-weight:850; letter-spacing:-2px; line-height:1.05; }
        .cf-login-brand span { color:#0daaa4; }
        .cf-login-kicker { color:#174875; font-weight:800; letter-spacing:2px; font-size:13px; margin-top:10px; }
        .cf-login-sub { color:#31577e; font-size:17px; margin-top:15px; }
        .cf-feature { display:flex; gap:15px; align-items:center; margin:22px 0; color:#123e70; }
        .cf-feature-icon { width:54px; height:54px; flex:0 0 54px; display:flex; align-items:center; justify-content:center; border-radius:50%; background:linear-gradient(145deg,#d9f9f6,#cfe6ff); color:#078e9c; font-size:24px; font-weight:800; }
        .cf-feature-title { font-size:16px; font-weight:750; }
        .cf-feature-copy { font-size:13px; color:#6382a4; margin-top:3px; }
        .cf-login-card { background:rgba(255,255,255,.84); border:1px solid rgba(255,255,255,.95); border-radius:24px; padding:25px 28px 15px; box-shadow:0 18px 55px rgba(24,94,150,.17); }
        .cf-card-brand { text-align:center; font-size:34px; font-weight:850; color:#103e75; letter-spacing:-1px; }
        .cf-card-brand span { color:#0daaa4; }
        .cf-card-tag { text-align:center; color:#31577e; font-size:10px; font-weight:800; letter-spacing:1.4px; margin-bottom:22px; }
        .cf-card-title { color:#103e75; font-size:28px; font-weight:800; margin:8px 0 2px; }
        .cf-card-copy { color:#58799d; font-size:14px; margin-bottom:16px; }
        div[data-testid="stForm"] { background:transparent; border:0; padding:0; }
        div[data-testid="stTextInput"] input { background:rgba(255,255,255,.9); border:1px solid #c9dff3; border-radius:11px; min-height:48px; }
        div[data-testid="stFormSubmitButton"] button { background:linear-gradient(90deg,#20c6b6,#008b99); color:white; border:0; border-radius:10px; min-height:48px; font-weight:750; }
        div[data-testid="stFormSubmitButton"] button:hover { border:1px solid #087d91; color:white; }
        div[data-testid="stTabs"] button { color:#245783; font-weight:700; }
        .cf-security-note { text-align:center; color:#6785a5; font-size:11px; padding:16px 0 4px; }
        @media(max-width:850px) {
          .block-container { padding-left:1rem; padding-right:1rem; }
          .cf-login-card { padding:20px 16px 12px; }
          .cf-login-brand { font-size:38px; }
          .cf-feature { margin:14px 0; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")

    with left:
        st.markdown(
            """
            <div style="padding:18px 8px 14px;">
              <div style="font-size:clamp(42px,4.6vw,68px);line-height:1;margin-bottom:8px;">💙</div>
              <div class="cf-login-brand">Care<span>Flow</span></div>
              <div class="cf-login-kicker">CLINICAL PATHWAY PROCESS MINING</div>
              <div class="cf-login-sub">Smarter pathways. Better care.</div>
              <div style="height:22px"></div>
              <div class="cf-feature"><div class="cf-feature-icon">⌁</div><div><div class="cf-feature-title">Process Mining</div><div class="cf-feature-copy">Discover. Analyze. Improve.</div></div></div>
              <div class="cf-feature"><div class="cf-feature-icon">⌘</div><div><div class="cf-feature-title">Clinical Pathways</div><div class="cf-feature-copy">Standardize. Optimize. Deliver.</div></div></div>
              <div class="cf-feature"><div class="cf-feature-icon">♧</div><div><div class="cf-feature-title">Care Teams</div><div class="cf-feature-copy">Collaborate. Coordinate. Care.</div></div></div>
              <div class="cf-feature"><div class="cf-feature-icon">⛨</div><div><div class="cf-feature-title">Governance</div><div class="cf-feature-copy">Secure. Compliant. Trusted.</div></div></div>
              <div style="margin-top:30px;color:#17648c;font-weight:700;font-size:14px;">Better data　→　Smarter decisions　→　Healthier tomorrows</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="cf-login-card">
              <div class="cf-card-brand">♥ Care<span>Flow</span></div>
              <div class="cf-card-tag">CLINICAL PATHWAY PROCESS MINING</div>
              <div class="cf-card-title">Welcome Back</div>
              <div class="cf-card-copy">Sign in to access your clinical analytics workspace.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        login_tab, signup_tab = st.tabs(["Login", "Create new account"])

        with login_tab:
            with st.form("careflow_login_form"):
                login_email = st.text_input("✉  Email address", placeholder="Enter your email address")
                login_password = st.text_input("♙  Password", type="password", placeholder="Enter your password")
                login_submit = st.form_submit_button("➜  Login", use_container_width=True)

            if login_submit:
                try:
                    result = supabase.auth.sign_in_with_password({
                        "email": login_email.strip(),
                        "password": login_password
                    })
                    if result.session and result.user:
                        st.session_state.careflow_user = {
                            "id": result.user.id,
                            "email": result.user.email
                        }
                        st.rerun()
                    else:
                        st.error("Login unsuccessful. Please try again.")
                except Exception:
                    st.error("Login failed. Check your email and password or verify your email address.")

        with signup_tab:
            st.caption("Create an account to access your CareFlow workspace.")
            with st.form("careflow_signup_form"):
                signup_email = st.text_input("✉  Email address", placeholder="Enter your email address")
                signup_password = st.text_input("♙  Create password", type="password", placeholder="At least 8 characters")
                confirm_password = st.text_input("♙  Confirm password", type="password", placeholder="Re-enter your password")
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
                        result = supabase.auth.sign_up({
                            "email": signup_email.strip(),
                            "password": signup_password
                        })
                        if result.session and result.user:
                            st.session_state.careflow_user = {
                                "id": result.user.id,
                                "email": result.user.email
                            }
                            st.success("Account created successfully.")
                            st.rerun()
                        else:
                            st.success("Registration received. Check your email to verify your account, then log in.")
                    except Exception:
                        st.error("Signup failed. Check your email, password requirements, and Supabase authentication settings.")

        st.markdown('<div class="cf-security-note">♧ Secure access　•　Your account, your control</div>', unsafe_allow_html=True)

    st.stop()

# Authenticated users can access the existing dashboard.
with st.sidebar:
    st.markdown(
        """
        <div style="font-size:22px;font-weight:800;
                    color:#ffffff;padding:8px 0 16px;">
            ☰ CareFlow
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Signed in as: "
        + str(st.session_state.careflow_user["email"])
    )

    if st.button("Log out", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.careflow_user = None
        st.rerun()

# ---------- END CAREFLOW AUTHENTICATION ----------


st.markdown("""
<style>
:root {
    --cf-navy: #102746;
    --cf-blue: #2563eb;
    --cf-teal: #0f9d9a;
    --cf-ink: #172b4d;
    --cf-muted: #64748b;
    --cf-border: #e3eaf3;
    --cf-surface: #ffffff;
}
.block-container {
    width: 100%;
    max-width: 1640px;
    padding-top: 1.15rem;
    padding-left: clamp(.75rem, 2.2vw, 2.2rem);
    padding-right: clamp(.75rem, 2.2vw, 2.2rem);
    padding-bottom: 2.5rem;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f5f8fc 0%, #ffffff 340px);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d2039 0%, #143b61 60%, #155e75 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * { color: #f7fbff; }
[data-testid="stSidebar"] button {
    background: rgba(255,255,255,.09) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,.17) !important;
    border-radius: 12px !important;
    font-weight: 650 !important;
    transition: all .18s ease;
}
[data-testid="stSidebar"] button:hover {
    background: rgba(20,184,166,.22) !important;
    border-color: #5eead4 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: 7px; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.18); }
[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    color: #cfe0f4 !important;
    font-size: .72rem !important;
    letter-spacing: .09em;
    text-transform: uppercase;
    font-weight: 800 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 12px;
    padding: .55rem .7rem;
    margin: 2px 0;
    border: 1px solid transparent;
    transition: background .18s ease, transform .18s ease, border-color .18s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,.10);
    border-color: rgba(153,246,228,.28);
    transform: translateX(2px);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(100deg, rgba(59,130,246,.38), rgba(13,148,136,.30));
    border: 1px solid rgba(153,246,228,.38);
    box-shadow: inset 3px 0 0 #5eead4;
}
.hero {
    position: relative;
    padding: clamp(1.2rem, 2.8vw, 2rem);
    border-radius: 22px;
    background: linear-gradient(120deg, #102746 0%, #1d4f91 62%, #087f8c 100%);
    color: #fff;
    margin: .2rem 0 1.25rem;
    overflow: hidden;
    box-shadow: 0 12px 32px rgba(16,39,70,.13);
    border: 1px solid rgba(255,255,255,.18);
}
.hero:after {
    content: "";
    position: absolute;
    width: 210px;
    height: 210px;
    right: -55px;
    top: -105px;
    border-radius: 50%;
    border: 28px solid rgba(255,255,255,.08);
    pointer-events: none;
}
.hero h1 {
    color: #fff;
    margin: 0;
    font-size: clamp(1.5rem, 3vw, 2.15rem);
    letter-spacing: -.035em;
    overflow-wrap: anywhere;
}
.hero p { color: #dcecff; margin: .55rem 0 0; font-size: clamp(.88rem, 1.4vw, 1.02rem); }
h1, h2, h3 { color: var(--cf-ink); letter-spacing: -.02em; overflow-wrap: anywhere; }
h2 { margin-top: .5rem; }
hr { border-color: var(--cf-border); }
.metric-card {
    border: 1px solid var(--cf-border);
    border-radius: 17px;
    background: linear-gradient(145deg, #fff 0%, #f9fbff 100%);
    padding: clamp(14px, 1.7vw, 19px);
    min-height: 108px;
    box-shadow: 0 5px 18px rgba(16,39,70,.045);
    overflow-wrap: anywhere;
    transition: transform .18s ease, box-shadow .18s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(16,39,70,.09);
}
.metric-label { color: var(--cf-muted); font-size: .84rem; font-weight: 600; }
.metric-value { color: var(--cf-navy); font-size: clamp(1.35rem, 2.4vw, 1.9rem); font-weight: 800; letter-spacing: -.035em; margin-top: .25rem; }
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"], [data-testid="stTable"] { width: 100%; max-width: 100%; }
[data-testid="stPlotlyChart"] {
    border: 1px solid #edf1f7;
    border-radius: 16px;
    background: rgba(255,255,255,.75);
    padding: 4px;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--cf-border) !important;
    border-radius: 16px !important;
}
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {
    min-height: 2.75rem;
    border-radius: 11px;
    font-weight: 650;
    transition: all .18s ease;
}
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: linear-gradient(100deg, #2563eb, #0f9d9a);
    border: 0;
    color: white;
}
.stButton button:hover, .stDownloadButton button:hover {
    border-color: #0f9d9a;
}
[data-baseweb="input"] > div, [data-baseweb="textarea"] > div,
[data-baseweb="select"] > div {
    border-radius: 11px !important;
    border-color: #d7e1ee !important;
}
[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,.12);
}
[data-baseweb="tab-list"] { gap: 8px; }
[data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    font-weight: 650;
}
[data-testid="stAlert"] { border-radius: 12px; }
@media (max-width: 900px) {
    .block-container { padding-top: .7rem; padding-left: .75rem; padding-right: .75rem; }
    .hero { border-radius: 17px; margin-bottom: .9rem; }
    .metric-card { min-height: 90px; }
    [data-testid="stPlotlyChart"] { overflow: hidden; }
    [data-testid="stSidebar"] { min-width: 0; }
    [data-testid="stDataFrame"] { overflow-x: auto; }
}
@media (max-width: 600px) {
    .block-container { padding-left: .55rem; padding-right: .55rem; }
    .hero { padding: 1rem; border-radius: 14px; }
    .hero h1 { font-size: 1.4rem; line-height: 1.25; }
    .hero p { font-size: .82rem; line-height: 1.5; }
    .metric-card { padding: 11px; min-height: 82px; border-radius: 12px; }
    .metric-label { font-size: .74rem; }
    .metric-value { font-size: 1.22rem; }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] { gap: .55rem; }
    h2 { font-size: 1.18rem !important; }
    h3 { font-size: 1.02rem !important; }
    .stSelectbox, .stMultiSelect, .stDateInput { width: 100%; }
    [data-testid="stPlotlyChart"] { padding: 0; border-radius: 12px; }
}
@media (prefers-reduced-motion: reduce) {
    *, *:before, *:after { transition: none !important; scroll-behavior: auto !important; }
}

/* ---------- CAREFLOW PREMIUM VISUAL POLISH ---------- */
:root {
    --cf-navy: #0b1f3a;
    --cf-blue: #2563eb;
    --cf-teal: #0d9488;
    --cf-ink: #132743;
    --cf-muted: #64748b;
    --cf-border: #dce6f2;
}
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(ellipse at 8% 0%, rgba(37,99,235,.07), transparent 32%),
      radial-gradient(ellipse at 95% 12%, rgba(13,148,136,.06), transparent 27%),
      #f6f9fd;
}
.block-container { max-width: 1720px; }
/* Strong sidebar overrides: prevent Streamlit defaults from making the menu white */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: linear-gradient(160deg, #091a31 0%, #12385b 58%, #0d5967 100%) !important;
    box-shadow: 8px 0 30px rgba(8, 26, 49, .10);
}
section[data-testid="stSidebar"] [data-testid="stExpander"],
section[data-testid="stSidebar"] [data-testid="stExpander"] details,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
    background: transparent !important;
    color: #f7fbff !important;
    border-color: rgba(255,255,255,.18) !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    color: #cfe0f4 !important;
    font-size: .72rem;
    letter-spacing: .09em;
    text-transform: uppercase;
    font-weight: 800;
}
section[data-testid="stSidebar"] [role="radiogroup"] { gap: 7px; }
section[data-testid="stSidebar"] [role="radiogroup"] label {
    background: rgba(255,255,255,.055) !important;
    color: #f7fbff !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: 12px;
    padding: .65rem .75rem;
    margin: 3px 0;
    transition: background .18s ease, transform .18s ease, border-color .18s ease;
}
section[data-testid="stSidebar"] [role="radiogroup"] label p,
section[data-testid="stSidebar"] [role="radiogroup"] label span {
    color: #f7fbff !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(45,212,191,.16) !important;
    border-color: rgba(94,234,212,.65) !important;
    transform: translateX(2px);
}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(100deg, rgba(59,130,246,.48), rgba(13,148,136,.40)) !important;
    border: 1px solid rgba(153,246,228,.55) !important;
    box-shadow: inset 3px 0 0 #5eead4;
}
.hero {
    background: linear-gradient(112deg, #0b1f3a 0%, #174d83 54%, #078b8a 100%);
    border: 1px solid rgba(255,255,255,.24);
    border-radius: 24px;
    box-shadow: 0 14px 34px rgba(16,39,70,.15);
}
.hero h1 { text-shadow: 0 2px 12px rgba(0,0,0,.10); }
.metric-card {
    position: relative;
    border: 1px solid #e2eaf4;
    background: linear-gradient(145deg, #ffffff 0%, #f8fbff 100%);
    box-shadow: 0 7px 22px rgba(15, 42, 75, .055);
}
.metric-card:before {
    content: "";
    position: absolute;
    left: 0; top: 15px; bottom: 15px;
    width: 4px;
    border-radius: 0 5px 5px 0;
    background: linear-gradient(180deg, #3b82f6, #14b8a6);
}
.metric-card:hover { border-color: #b9d5ee; }
[data-testid="stPlotlyChart"] {
    border: 1px solid #e4ebf4;
    border-radius: 18px;
    background: #fff;
    box-shadow: 0 6px 20px rgba(15,42,75,.035);
    padding: 8px;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid #e2eaf4;
    border-radius: 14px;
    overflow: hidden;
    background: #fff;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.82);
    border-color: #e1e9f3 !important;
    border-radius: 18px !important;
    box-shadow: 0 5px 18px rgba(15,42,75,.035);
}
[data-testid="stForm"] {
    border: 1px solid #e2eaf4;
    border-radius: 18px;
    padding: clamp(14px, 2vw, 24px);
    background: linear-gradient(145deg, #fff, #f8fbff);
    box-shadow: 0 12px 28px rgba(15,42,75,.06);
}
[data-baseweb="tab-list"] {
    background: #edf3fa;
    border-radius: 13px;
    padding: 5px;
}
[data-baseweb="tab"] { border-radius: 9px !important; }
[data-baseweb="tab"][aria-selected="true"] {
    background: #fff !important;
    box-shadow: 0 2px 8px rgba(15,42,75,.09);
}
.stButton button, .stDownloadButton button,
[data-testid="stFormSubmitButton"] button {
    border-radius: 12px;
    font-weight: 700;
    box-shadow: 0 3px 9px rgba(37,99,235,.06);
}
[data-testid="stAlert"] { border-radius: 14px; }
[data-testid="stCaptionContainer"] { color: #718198; }
@media (max-width: 600px) {
    .hero { border-radius: 16px; }
    [data-testid="stPlotlyChart"] { padding: 2px; border-radius: 12px; }
    [data-testid="stForm"] { padding: 12px; border-radius: 14px; }
}


/* Premium polish layer */
[data-testid="stHeader"] { background: rgba(245,248,252,.82); }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
 border-radius:12px!important; min-height:2.7rem; font-weight:650!important;
 border:1px solid #d5e1ee!important; transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease;
}
.stButton > button:hover,.stDownloadButton > button:hover,[data-testid="stFormSubmitButton"] > button:hover {
 transform:translateY(-1px);box-shadow:0 7px 18px rgba(16,39,70,.10);border-color:#0f9d9a!important;
}
div[data-testid="stTabs"] button[role="tab"] { border-radius:10px 10px 0 0;font-weight:650; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#fff,#f7fbff);border:1px solid #e3eaf3;border-radius:15px;padding:13px 15px;box-shadow:0 4px 14px rgba(16,39,70,.035); }
div[data-testid="stMetric"] label { color:#64748b!important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#102746;font-weight:800; }
[data-testid="stExpander"] { border:1px solid #e3eaf3;border-radius:14px;overflow:hidden;background:rgba(255,255,255,.78); }
[data-testid="stDataFrame"] { border:1px solid #e3eaf3;border-radius:13px;overflow:hidden; }
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"],.stMultiSelect [data-baseweb="select"] { border-radius:11px!important; }
div[data-testid="stAlert"] { border-radius:13px; }
.cf-feature-card { background:linear-gradient(145deg,#fff,#f7fbff);border:1px solid #e3eaf3;border-radius:17px;padding:18px;min-height:128px;box-shadow:0 5px 18px rgba(16,39,70,.045); }
.cf-feature-title { color:#102746;font-size:1.02rem;font-weight:800;margin-bottom:7px; }
.cf-feature-copy { color:#64748b;font-size:.88rem;line-height:1.5; }
@media(max-width:760px) {
 .block-container{padding-left:.6rem;padding-right:.6rem;padding-top:.7rem}
 .hero{border-radius:16px;padding:1.05rem}
 .metric-card{min-height:82px;padding:12px}
 div[data-testid="stMetric"]{padding:10px 11px}
 [data-testid="stPlotlyChart"]{padding:0}
 .cf-feature-card{padding:14px;min-height:110px}
}

</style>
""", unsafe_allow_html=True)

def load_csvs():
    candidates = [Path("careflow_event_log.csv"), Path("event_log_ED_MMA_2026.csv"), Path("sample_event_log.csv")]
    for p in candidates:
        if p.exists():
            try:
                d = pd.read_csv(p)
                if not d.empty:
                    return d, p.name
            except Exception:
                pass
    return pd.DataFrame(), "No CSV found"

def find_col(df, hints):
    for c in df.columns:
        cl = str(c).strip().lower().replace("_"," ").replace("-"," ")
        if any(h in cl for h in hints):
            return c
    return None

df, source_name = load_csvs()

with st.sidebar:
    st.markdown(
    """
    <div style="padding:12px 4px 18px;">
        <div style="font-size:28px;font-weight:800;color:#ffffff;">
            ♥ CareFlow
        </div>
        <div style="font-size:12px;color:#bfdbfe;margin-top:6px;">
            CLINICAL ANALYTICS
        </div>
        <div style="font-size:13px;color:#e2e8f0;margin-top:8px;">
            Smarter pathways. Better care.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)    
    with st.expander("☰ Menu", expanded=True):
        page = st.radio(
            "CareFlow Navigation",
            [
                "Executive Dashboard",
                "Hospital Operations Dashboard",
                "Process Mining Explorer",
                "Patient Flow",
                "Clinical Pathways",
                "Bed & Discharge Management",
                "Task & Escalation Center",
                "Care coordination",
                "Care Teams",
                "Reports & Outcomes",
                "Pathway Comparison",
                "Data Quality Studio",
                "Data Dictionary",
                "Notifications Center",
                "Insights & Benchmarks",
                "Saved Workspace",
                "Display Preferences",
                "Security & Governance",
                "Help Center",
                "Profile",
            ],
            key="careflow_workspace_menu",
            label_visibility="collapsed",
        )
        st.divider()
    st.caption("Clinical Pathway Process Mining")
    st.caption("Data source: " + source_name)
    # Department availability is determined after loading and inspecting the event log.

st.markdown(f'<div class="hero"><div style="font-size:.72rem;letter-spacing:.15em;font-weight:800;color:#99f6e4;margin-bottom:.55rem">CLINICAL ANALYTICS WORKSPACE</div><h1>CareFlow <span style="font-weight:450;font-size:clamp(.95rem,2vw,1.15rem);opacity:.92">/ {page}</span></h1><p>Turn event-log data into clearer operational insights and pathway visibility.</p></div>', unsafe_allow_html=True)

if df.empty:
    st.error("No event-log CSV was found. Put careflow_event_log.csv or event_log_ED_MMA_2026.csv beside app.py in your GitHub repository.")
    st.stop()

# Normalize column roles from the uploaded event log, while preserving original columns.
case_col = find_col(df, ["case id","case_id","patient id","patient_id","encounter","visit id","case"])
activity_col = find_col(df, ["activity","event","procedure","step","action"])
time_col = find_col(df, ["timestamp","datetime","date time","event time","time"])
dept_col = find_col(df, ["department","dept","unit","ward","service line"])
status_col = find_col(df, ["status","outcome","state"])
staff_col = find_col(df, ["resource","staff","clinician","doctor","nurse","assignee","user"])

# The uploaded event logs do not contain a department column. To populate the
# Departments view, assign reproducible DEMO department labels by visit/case ID.
# These are synthetic labels for the dashboard and are not source clinical facts.
synthetic_department = False
if dept_col is None:
    key_col = case_col if case_col else (find_col(df, ["patient id","patient_id"]) or df.columns[0])
    dept_names = ["Emergency", "Cardiology", "Respiratory", "Neurology", "Orthopedics", "General Medicine"]
    keys = df[key_col].fillna("Unknown").astype(str)
    df["demo_department"] = keys.map(lambda x: dept_names[sum((i + 1) * ord(ch) for i, ch in enumerate(x)) % len(dept_names)])
    dept_col = "demo_department"
    synthetic_department = True

if synthetic_department:
    with st.sidebar:
        st.caption("Department labels are synthetic demo assignments; the source file has no department field.")

# Filter controls
f1, f2 = st.columns([2,1])
with f1:
    if dept_col:
        departments = ["All departments"] + sorted(df[dept_col].dropna().astype(str).unique().tolist())
        chosen_dept = st.selectbox("Department", departments)
    else:
        chosen_dept = "All departments"
with f2:
    st.caption(f"Loaded **{len(df):,}** event records · **{len(df.columns)}** fields")

filtered = df.copy()
if dept_col and chosen_dept != "All departments":
    filtered = filtered[filtered[dept_col].astype(str) == chosen_dept]

n_events = len(filtered)
n_cases = filtered[case_col].nunique() if case_col else n_events
n_activities = filtered[activity_col].nunique() if activity_col else 0
n_departments = filtered[dept_col].nunique() if dept_col else 0

if page == "Executive Dashboard":
    st.subheader("Clinical analytics overview")
    st.caption("Explore event activity in the currently selected dataset.")

    if activity_col:
        activity_options = sorted(
            filtered[activity_col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        selected_activities = st.multiselect(
            "Filter by activity",
            options=activity_options,
            default=activity_options,
            key="dashboard_activity_filter"
        )
        dashboard_data = filtered[
            filtered[activity_col].fillna("Unknown").astype(str).isin(
                selected_activities
            )
        ]
    else:
        dashboard_data = filtered.copy()

    # Optional date-range filter for clinical event analytics
    if time_col:
        dashboard_data[time_col] = pd.to_datetime(
            dashboard_data[time_col], errors="coerce"
        )
        valid_dates = dashboard_data[time_col].dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            date_range = st.date_input(
                "Filter by event date",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="dashboard_date_filter",
            )

            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range
                dashboard_data = dashboard_data[
                    dashboard_data[time_col].dt.date.between(
                        start_date, end_date
                    )
                ]

    filtered = dashboard_data
    n_events = len(filtered)
    n_cases = filtered[case_col].nunique() if case_col else 0
    n_activities = (
        filtered[activity_col].nunique() if activity_col else 0
    )
    n_departments = (
        filtered[dept_col].nunique() if dept_col else 0
    )
    m = st.columns(4)
    cards = [
        ("Cases / patients", f"{n_cases:,}"),
        ("Event records", f"{n_events:,}"),
        ("Unique activities", f"{n_activities:,}" if activity_col else "—"),
        ("Departments", f"{n_departments:,}" if dept_col else "—"),
    ]
    for c,(label,value) in zip(m,cards):
        c.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)
    left,right = st.columns([1.35,1])
    with left:
        st.subheader("Most frequent activities")
        if activity_col:
            counts = filtered[activity_col].fillna("Unknown").astype(str).value_counts().head(15).rename_axis("Activity").reset_index(name="Events")
            fig = px.bar(counts, x="Events", y="Activity", orientation="h", color="Events", color_continuous_scale="Blues")
            fig.update_layout(height=400, margin=dict(l=5,r=5,t=15,b=5), yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("No activity/event column detected. The raw event log is shown below.")
    with right:
        st.subheader("Events by department")
        if dept_col:
            counts = filtered[dept_col].fillna("Unknown").astype(str).value_counts().reset_index()
            counts.columns = ["Department","Events"]
            fig = px.pie(counts,names="Department",values="Events",hole=.58)
            fig.update_layout(height=400,margin=dict(l=5,r=5,t=15,b=5))
            st.plotly_chart(fig,use_container_width=True)
        elif status_col:
            counts = filtered[status_col].fillna("Unknown").astype(str).value_counts().reset_index()
            counts.columns = ["Status","Events"]
            st.plotly_chart(px.pie(counts,names="Status",values="Events",hole=.58),use_container_width=True)
        else:
            st.info("No department/status column detected.")
    left,right = st.columns(2)
    with left:
        st.subheader("Event activity over time")
        if time_col:
            tmp = filtered.copy()
            tmp[time_col] = pd.to_datetime(tmp[time_col], errors="coerce")
            tmp = tmp.dropna(subset=[time_col])
            if len(tmp):
                tmp["Date"] = tmp[time_col].dt.date
                trend = tmp.groupby("Date").size().reset_index(name="Events")
                st.plotly_chart(px.line(trend,x="Date",y="Events",markers=True),use_container_width=True)
            else: st.info("The detected time column could not be parsed as dates.")
        else: st.info("No timestamp column detected.")
    with right:
        st.subheader("Event log preview")
        st.dataframe(filtered.head(12),use_container_width=True,hide_index=True)

elif page == "Hospital Operations Dashboard":
    st.subheader("Hospital Operations & Patient Flow Analytics")
    st.caption("All values and charts below are calculated from the currently loaded event log and selected department. Missing source fields are not estimated.")

    # Optional filters are derived from the actual source columns.
    ops = filtered.copy()
    if time_col:
        ops[time_col] = pd.to_datetime(ops[time_col], errors="coerce")
        valid_time = ops[time_col].dropna()
        if not valid_time.empty:
            d1, d2 = st.columns(2)
            with d1:
                start = st.date_input("Start date", value=valid_time.min().date(), min_value=valid_time.min().date(), max_value=valid_time.max().date(), key="ops_start_date")
            with d2:
                end = st.date_input("End date", value=valid_time.max().date(), min_value=valid_time.min().date(), max_value=valid_time.max().date(), key="ops_end_date")
            if start <= end:
                ops = ops[ops[time_col].dt.date.between(start, end)]
            else:
                st.warning("Start date must be on or before end date.")
                ops = ops.iloc[0:0]

    total_events = len(ops)
    total_cases = int(ops[case_col].nunique()) if case_col else None
    total_activities = int(ops[activity_col].nunique()) if activity_col else None
    avg_events_case = float(ops.groupby(case_col).size().mean()) if case_col and not ops.empty else None
    kpis = st.columns(4)
    kpis[0].metric("Event records", f"{total_events:,}")
    kpis[1].metric("Distinct cases", f"{total_cases:,}" if total_cases is not None else "Not available")
    kpis[2].metric("Unique activities", f"{total_activities:,}" if total_activities is not None else "Not available")
    kpis[3].metric("Mean events per case", f"{avg_events_case:.2f}" if avg_events_case is not None else "Not available")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Events by recorded activity")
        if activity_col and not ops.empty:
            activity_counts = ops[activity_col].fillna("Unknown").astype(str).value_counts().head(15).rename_axis("Activity").reset_index(name="Event records")
            st.plotly_chart(px.bar(activity_counts, x="Event records", y="Activity", orientation="h", color="Event records", title="Most frequent recorded activities"), use_container_width=True)
        else:
            st.info("Activity counts unavailable: an activity/event field was not detected or no rows match the filters.")
    with right:
        st.markdown("#### Recorded event distribution")
        category_col = (status_col if synthetic_department else (dept_col or status_col))
        if category_col and not ops.empty:
            dist = ops[category_col].fillna("Unknown").astype(str).value_counts().head(12).rename_axis(str(category_col)).reset_index(name="Event records")
            st.plotly_chart(px.pie(dist, names=str(category_col), values="Event records", hole=0.55, title=f"Event records by {category_col}"), use_container_width=True)
        else:
            st.info("Distribution unavailable: no department or status/outcome field was detected.")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Event volume over time")
        if time_col:
            timed = ops.dropna(subset=[time_col]).copy()
            if not timed.empty:
                timed["Date"] = timed[time_col].dt.date
                trend = timed.groupby("Date").size().reset_index(name="Event records")
                st.plotly_chart(px.line(trend, x="Date", y="Event records", markers=True, title="Observed event records by date"), use_container_width=True)
            else:
                st.info("No valid timestamps are available in the selected rows.")
        else:
            st.info("Time trend unavailable: no timestamp field was detected.")
    with right:
        st.markdown("#### Case duration (if timestamps support it)")
        if case_col and time_col:
            case_dates = ops.dropna(subset=[time_col]).groupby(case_col)[time_col].agg(["min", "max"])
            case_dates["Duration hours"] = (case_dates["max"] - case_dates["min"]).dt.total_seconds() / 3600
            case_dates = case_dates[case_dates["Duration hours"] >= 0]
            if not case_dates.empty:
                st.metric("Cases with usable timestamps", f"{len(case_dates):,}")
                st.metric("Median observed case span (hours)", f"{case_dates['Duration hours'].median():,.2f}")
                st.plotly_chart(px.histogram(case_dates.reset_index(), x="Duration hours", nbins=25, title="Distribution of observed case spans"), use_container_width=True)
            else:
                st.info("Case spans cannot be calculated from the available timestamps.")
        else:
            st.info("Case duration requires both case/encounter and timestamp fields.")

    st.markdown("#### Source data preview")
    st.caption(f"Source file: {source_name} · Rows in this view: {len(ops):,} · These are operational event-log measures, not clinical outcomes or external benchmarks.")
    st.dataframe(ops.head(100), use_container_width=True, hide_index=True)
    st.download_button("Export current dashboard rows", ops.to_csv(index=False).encode("utf-8"), "careflow_hospital_operations_view.csv", "text/csv")

elif page == "Task & Escalation Center":
    st.subheader("Task & Escalation Center")
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

elif page == "Reports & Outcomes":
    st.subheader("▥ Reports")
    st.write("Generate an overview from the uploaded event log.")
    a,b,c=st.columns(3)
    a.metric("Event records",f"{n_events:,}")
    b.metric("Cases / patients",f"{n_cases:,}")
    c.metric("Activities",f"{n_activities:,}" if activity_col else "Not detected")
    st.dataframe(filtered.describe(include="all").transpose().reset_index(names="Field"),use_container_width=True)
    if case_col and time_col:
        outcome_tmp = filtered.copy()
        outcome_tmp[time_col] = pd.to_datetime(outcome_tmp[time_col], errors="coerce")
        case_times = outcome_tmp.dropna(subset=[time_col]).groupby(case_col)[time_col].agg(["min", "max"])
        if not case_times.empty:
            case_times["Observed elapsed hours"] = (case_times["max"] - case_times["min"]).dt.total_seconds() / 3600
            o1,o2 = st.columns(2)
            o1.metric("Cases with usable timestamps", f"{len(case_times):,}")
            o2.metric("Median observed elapsed time", f"{case_times['Observed elapsed hours'].median():,.1f} h")
            st.caption("Elapsed time is the span between first and last recorded event, not necessarily hospital length of stay.")
    st.download_button("Download filtered event log CSV",filtered.to_csv(index=False).encode("utf-8"),"careflow_filtered_event_log.csv","text/csv")

elif page == "Care coordination":
    st.subheader("Care coordination")
    st.write("Department-level overview based on the available fields in the uploaded data.")
    if dept_col:
        d = filtered[dept_col].fillna("Unknown").astype(str).value_counts().rename_axis("Department").reset_index(name="Event records")
        st.dataframe(d,use_container_width=True,hide_index=True)
        st.plotly_chart(px.bar(d,x="Department",y="Event records",color="Event records"),use_container_width=True)
    else:
        st.info("Your current event log does not appear to contain a department field. The original columns are listed below.")
        st.write(list(df.columns))

elif page == "Process Mining Explorer":
    st.subheader("Process Mining Explorer")
    st.caption("Explore observed event sequences in your selected event log. This describes recorded workflow; it does not recommend clinical treatment.")
    if case_col and activity_col:
        work = filtered.copy()
        if time_col:
            work[time_col] = pd.to_datetime(work[time_col], errors="coerce")
            work = work.sort_values(time_col, kind="stable", na_position="last")
        work[activity_col] = work[activity_col].fillna("Unknown activity").astype(str)
        st.markdown("#### Most frequent observed transitions")
        work["Next activity"] = work.groupby(case_col)[activity_col].shift(-1)
        transitions = work.dropna(subset=["Next activity"]).groupby([activity_col, "Next activity"]).size().reset_index(name="Transitions")
        transitions = transitions.rename(columns={activity_col:"From activity", "Next activity":"To activity"}).sort_values("Transitions", ascending=False)
        if transitions.empty:
            st.info("There are not enough consecutive events within a case to calculate transitions.")
        else:
            st.plotly_chart(px.bar(transitions.head(15), x="Transitions", y="From activity", color="To activity", orientation="h", title="Most frequent recorded transitions"), use_container_width=True)
            st.dataframe(transitions.head(100), use_container_width=True, hide_index=True)
            st.download_button("Export transitions CSV", transitions.to_csv(index=False).encode("utf-8"), "careflow_transitions.csv", "text/csv")
            st.markdown("#### Observed process map")
            st.caption("Node links represent consecutive activities recorded in the event log. Link widths reflect observed transition counts.")
            top_links = transitions.head(40).copy()
            if not top_links.empty:
                nodes = list(dict.fromkeys(top_links["From activity"].tolist() + top_links["To activity"].tolist()))
                node_index = {name: i for i, name in enumerate(nodes)}
                import plotly.graph_objects as go
                process_fig = go.Figure(data=[go.Sankey(
                    arrangement="snap",
                    node=dict(label=nodes, pad=14, thickness=18),
                    link=dict(source=[node_index[v] for v in top_links["From activity"]],
                              target=[node_index[v] for v in top_links["To activity"]],
                              value=top_links["Transitions"].astype(int).tolist())
                )])
                process_fig.update_layout(height=560, margin=dict(l=8, r=8, t=20, b=8), font=dict(size=11))
                st.plotly_chart(process_fig, use_container_width=True)
        st.markdown("#### Case pathway variants")
        variants = work.groupby(case_col)[activity_col].agg(lambda x: " → ".join(x.astype(str))).value_counts().rename_axis("Observed pathway").reset_index(name="Cases")
        st.dataframe(variants.head(100), use_container_width=True, hide_index=True)
    else:
        st.info("This feature needs identifiable case/encounter and activity/event columns. Detected fields: " + ", ".join(map(str, df.columns)))
    st.caption("The analysis uses the uploaded event-log rows. Results depend on data completeness and event ordering.")

elif page == "Bed & Discharge Management":
    st.subheader("Bed & Discharge Management")
    st.caption("Operational indicators are shown only when the event log contains suitable fields. No bed availability is invented.")
    bed_col = find_col(df, ["bed status", "bed availability", "bed id", "bed number", "bed occupied"])
    discharge_col = find_col(df, ["discharge", "discharged at", "discharge date", "discharge time"])
    admission_col = find_col(df, ["admission", "admitted at", "admission date", "admission time"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Cases in current filter", f"{n_cases:,}")
    c2.metric("Admission field", "Available" if admission_col else "Not detected")
    c3.metric("Discharge field", "Available" if discharge_col else "Not detected")
    if bed_col:
        st.markdown("#### Recorded bed field values")
        bed_counts = filtered[bed_col].fillna("Unknown").astype(str).value_counts().rename_axis("Recorded value").reset_index(name="Records")
        st.plotly_chart(px.bar(bed_counts, x="Recorded value", y="Records", title="Recorded bed-related values"), use_container_width=True)
    else:
        st.info("No bed/occupancy field was detected in the uploaded event log, so bed occupancy and available-bed counts cannot be calculated.")
    if admission_col or discharge_col:
        cols = [c for c in [case_col, admission_col, discharge_col, dept_col, status_col] if c]
        st.dataframe(filtered[cols].drop_duplicates().head(500), use_container_width=True, hide_index=True)
    else:
        st.info("Add verified admission/discharge timestamps to the source data to enable discharge-delay analysis.")
    st.warning("This is an analytics view, not a live bed-management system. Confirm all operational figures against the hospital's authoritative system.")

elif page == "Patient Flow":
    st.subheader("♥ Patient Flow")
    if case_col and activity_col:
        flow = filtered.groupby(case_col)[activity_col].agg(lambda s:" → ".join(s.dropna().astype(str).head(12))).reset_index(name="Observed pathway")
        st.dataframe(flow,use_container_width=True,hide_index=True)
        st.caption("Activity order follows the file's current row order. For accurate sequence analysis, sort by timestamp when one is available.")
    else:
        st.info("Patient Flow needs recognizable case/patient ID and activity/event columns.")
    if time_col and case_col:
        tmp=filtered.copy(); tmp[time_col]=pd.to_datetime(tmp[time_col],errors="coerce")
        durations=tmp.dropna(subset=[time_col]).groupby(case_col)[time_col].agg(["min","max"])
        if len(durations):
            durations["Elapsed hours"]=(durations["max"]-durations["min"]).dt.total_seconds()/3600
            st.subheader("Observed case elapsed time")
            st.dataframe(durations.reset_index(),use_container_width=True,hide_index=True)

elif page == "Clinical Pathways":
    st.subheader("⌁ Clinical Pathways")
    if case_col and activity_col:
        temp=filtered.copy()
        if time_col:
            temp[time_col]=pd.to_datetime(temp[time_col],errors="coerce")
            temp=temp.sort_values(time_col,kind="stable")
        pathways=temp.groupby(case_col)[activity_col].agg(lambda s:" → ".join(s.dropna().astype(str))).value_counts().rename_axis("Observed pathway").reset_index(name="Cases")
        st.dataframe(pathways,use_container_width=True,hide_index=True)
        st.subheader("Most common observed pathways")
        st.plotly_chart(px.bar(pathways.head(12),x="Cases",y="Observed pathway",orientation="h",color="Cases"),use_container_width=True)
    else:
        st.info("Clinical Pathways needs recognizable case/patient ID and activity/event columns.")
    st.caption("These are observed sequences from the supplied event log, not clinical recommendations.")

elif page == "Care Teams":
    st.subheader("♙ Care Teams")
    if staff_col:
        cols=[c for c in [dept_col,staff_col] if c]
        team_view=filtered[cols].fillna("Unknown").drop_duplicates()
        st.dataframe(team_view,use_container_width=True,hide_index=True)
        st.caption("Staff/team fields are inferred from column names. Verify them before relying on the grouping.")
    else:
        st.info("No obvious staff/resource field was detected in the event log.")
        st.write("Available fields:",", ".join(map(str,df.columns)))
    if dept_col and staff_col:
        workload=filtered.groupby([dept_col,staff_col]).size().reset_index(name="Event records")
        st.plotly_chart(px.bar(workload,x=staff_col,y="Event records",color=dept_col,barmode="group"),use_container_width=True)

elif page == "Pathway Comparison":
    st.subheader("Pathway Comparison")
    st.caption("Compare observed event sequences from the selected event log. This is descriptive process analysis, not a clinical recommendation.")
    if case_col and activity_col:
        pathway_source = filtered.copy()
        if time_col:
            pathway_source[time_col] = pd.to_datetime(pathway_source[time_col], errors="coerce")
            pathway_source = pathway_source.sort_values(time_col, kind="stable", na_position="last")
        pathway_source[activity_col] = pathway_source[activity_col].fillna("Unknown activity").astype(str)
        pathway_counts = pathway_source.groupby(case_col)[activity_col].agg(lambda values: " → ".join(values.tolist())).value_counts().rename_axis("Observed pathway").reset_index(name="Cases")
        if not pathway_counts.empty:
            st.metric("Distinct observed pathways", f"{len(pathway_counts):,}")
            top_n = st.slider("Pathways to compare", min_value=2, max_value=min(20, max(2, len(pathway_counts))), value=min(8, max(2, len(pathway_counts))))
            compare_df = pathway_counts.head(top_n)
            st.plotly_chart(px.bar(compare_df, x="Cases", y="Observed pathway", orientation="h", color="Cases", title="Most frequent observed pathways"), use_container_width=True)
            st.dataframe(compare_df, use_container_width=True, hide_index=True)
            if len(pathway_counts) > 1:
                first_path = st.selectbox("Select a pathway to inspect", pathway_counts["Observed pathway"].tolist())
                selected_cases = pathway_source.groupby(case_col)[activity_col].agg(lambda values: " → ".join(values.tolist()))
                case_ids = selected_cases[selected_cases == first_path].index
                st.caption(f"Cases following this exact observed sequence: {len(case_ids):,}")
        else:
            st.info("No complete pathways could be assembled from the current filter.")
    else:
        st.info("Pathway comparison needs recognizable case/encounter ID and activity/event columns.")

elif page == "Data Quality Studio":
    st.subheader("Data Quality Studio")
    st.caption("Review missing fields, duplicates, timestamp quality, and event-log readiness before interpreting analytics.")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows", f"{len(filtered):,}")
    q2.metric("Columns", f"{len(filtered.columns):,}")
    q3.metric("Duplicate rows", f"{int(filtered.duplicated().sum()):,}")
    q4.metric("Rows with missing values", f"{int(filtered.isna().any(axis=1).sum()):,}")
    missing_table = pd.DataFrame({"Field": filtered.columns.astype(str), "Missing values": [int(filtered[c].isna().sum()) for c in filtered.columns], "Missing %": [round(float(filtered[c].isna().mean() * 100), 2) for c in filtered.columns], "Unique values": [int(filtered[c].nunique(dropna=True)) for c in filtered.columns], "Detected role": ["Case ID" if c == case_col else "Activity" if c == activity_col else "Timestamp" if c == time_col else "Department" if c == dept_col else "Status" if c == status_col else "Staff/resource" if c == staff_col else "Other" for c in filtered.columns]})
    st.dataframe(missing_table, use_container_width=True, hide_index=True)
    if time_col:
        parsed_times = pd.to_datetime(filtered[time_col], errors="coerce")
        invalid_times = int(parsed_times.isna().sum())
        t1, t2 = st.columns(2)
        t1.metric("Unparseable timestamps", f"{invalid_times:,}")
        t2.metric("Timestamp parse success", f"{(100 * parsed_times.notna().mean()):.1f}%" if len(parsed_times) else "N/A")
        if case_col and activity_col:
            event_check = filtered[[case_col, activity_col]].copy()
            event_check["Case ID missing"] = event_check[case_col].isna()
            event_check["Activity missing"] = event_check[activity_col].isna()
            st.caption("Process-mining readiness: case and activity columns are detected. Confirm that case IDs are pseudonymized and events are correctly ordered before operational use.")
    else:
        st.warning("No timestamp column detected. Time-based pathway ordering and elapsed-time analysis may be unavailable.")
    st.download_button("Download data-quality report", missing_table.to_csv(index=False).encode("utf-8"), "careflow_data_quality_report.csv", "text/csv")

elif page == "Data Dictionary":
    st.subheader("Data Dictionary & Field Mapping")
    st.caption("Review the columns detected in your uploaded event log and map likely process-mining roles.")
    role_rows = []
    for col in df.columns:
        role_rows.append({"Source field": str(col), "Detected role": "Case / encounter identifier" if col == case_col else "Activity / event" if col == activity_col else "Timestamp" if col == time_col else "Department / unit" if col == dept_col and not synthetic_department else "Synthetic demo department (not source data)" if col == dept_col and synthetic_department else "Status / outcome" if col == status_col else "Staff / resource" if col == staff_col else "Unmapped", "Data type": str(df[col].dtype), "Example value": str(df[col].dropna().iloc[0])[:120] if df[col].notna().any() else "(all values missing)"})
    dictionary_df = pd.DataFrame(role_rows)
    st.dataframe(dictionary_df, use_container_width=True, hide_index=True)
    st.download_button("Export data dictionary", dictionary_df.to_csv(index=False).encode("utf-8"), "careflow_data_dictionary.csv", "text/csv")
    st.info("Automatic role detection is based on column names. Review mappings before making decisions. The app does not change your original uploaded file.")

elif page == "Notifications Center":
    st.subheader("Notifications Center")
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

elif page == "Insights & Benchmarks":
    st.subheader("Insights & Benchmarks")
    st.caption("Descriptive insights from the selected event log—not external hospital benchmarks or clinical recommendations.")
    a, b, c = st.columns(3)
    a.metric("Records in view", f"{len(filtered):,}")
    b.metric("Distinct cases", f"{filtered[case_col].nunique():,}" if case_col else "Not detected")
    c.metric("Missing-value cells", f"{int(filtered.isna().sum().sum()):,}")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Data completeness by field")
        completeness = pd.DataFrame({"Field": filtered.columns.astype(str), "Completeness (%)": [round(float(filtered[col].notna().mean()*100), 1) for col in filtered.columns]})
        completeness = completeness.sort_values("Completeness (%)")
        st.plotly_chart(px.bar(completeness.tail(18), x="Completeness (%)", y="Field", orientation="h", range_x=[0,100], color="Completeness (%)", color_continuous_scale="Teal"), use_container_width=True)
    with right:
        st.markdown("#### Event volume by activity")
        if activity_col:
            activity_summary = filtered[activity_col].fillna("Unknown").astype(str).value_counts().head(12).rename_axis("Activity").reset_index(name="Records")
            st.plotly_chart(px.bar(activity_summary, x="Records", y="Activity", orientation="h", color="Records", color_continuous_scale="Blues"), use_container_width=True)
        else:
            st.info("No activity column detected.")
    if case_col and activity_col:
        st.markdown("#### Events per case")
        per_case = filtered.groupby(case_col).size().rename("Events per case").reset_index()
        st.plotly_chart(px.histogram(per_case, x="Events per case", nbins=25), use_container_width=True)
        st.dataframe(per_case.describe().round(2).reset_index().rename(columns={"index":"Statistic"}), use_container_width=True, hide_index=True)
    st.info("Validate definitions and clinical context with qualified staff before operational use.")

elif page == "Saved Workspace":
    st.subheader("Saved Workspace")
    st.caption("Save a named snapshot of the current dataset and filters. Saved views are temporary and session-only.")
    if "careflow_saved_views" not in st.session_state:
        st.session_state.careflow_saved_views = []
    with st.form("careflow_saved_workspace_form", clear_on_submit=True):
        view_name = st.text_input("Workspace name", placeholder="e.g. Monthly pathway review")
        view_notes = st.text_area("Notes", placeholder="What are you reviewing?")
        save_view = st.form_submit_button("Save current workspace", use_container_width=True)
    if save_view:
        if view_name.strip():
            st.session_state.careflow_saved_views.insert(0, {"Name":view_name.strip(),"Page":page,"Data source":source_name,"Rows in current view":int(len(filtered)),"Department filter":str(chosen_dept),"Notes":view_notes.strip()})
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

elif page == "Display Preferences":
    st.subheader("Display Preferences")
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

elif page == "Security & Governance":
    st.subheader("◈ Governance")
    missing=filtered.isna().sum()
    quality=pd.DataFrame({"Field":filtered.columns,"Missing values":[int(missing[c]) for c in filtered.columns],"Missing %":[round(float(missing[c])/max(len(filtered),1)*100,1) for c in filtered.columns]})
    a,b,c=st.columns(3)
    a.metric("Rows",f"{len(filtered):,}")
    b.metric("Columns",f"{len(filtered.columns):,}")
    c.metric("Rows with any missing data",f"{int(filtered.isna().any(axis=1).sum()):,}")
    st.subheader("Data quality checks")
    st.dataframe(quality,use_container_width=True,hide_index=True)
    if case_col: st.info(f"Detected case identifier field: {case_col}")
    else: st.warning("Case identifier column was not detected automatically.")
    if activity_col: st.info(f"Detected activity field: {activity_col}")
    else: st.warning("Activity/event column was not detected automatically.")
    if time_col: st.info(f"Detected timestamp field: {time_col}")
    else: st.warning("Timestamp column was not detected automatically.")


elif page == "Help Center":
    st.subheader("CareFlow Help Center")
    st.caption("Guidance for using the analytics workspace and troubleshooting common issues.")
    q1,q2,q3 = st.columns(3)
    q1.metric("Help topics", "6")
    q2.metric("Support channel", "Form")
    q3.metric("Service status", "App session")
    with st.expander("How do I load my actual event log?", expanded=True):
        st.write("Place the approved CSV file beside app.py in the repository using one of the configured filenames: careflow_event_log.csv, event_log_ED_MMA_2026.csv, or sample_event_log.csv. Do not commit identifiable patient data to a public repository.")
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

elif page == "Profile":
    st.subheader("My CareFlow Profile")
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

st.divider()
st.caption("CareFlow is a clinical process analytics workspace, not a clinical decision-support system. Department labels are synthetic where indicated. Do not publish identifiable patient or health data to a public repository.")
