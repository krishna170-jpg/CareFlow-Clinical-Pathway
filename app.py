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
    <div style="
        text-align:center;
        padding:32px 20px;
        margin:10px 0 24px;
        background:linear-gradient(135deg,#102746,#2463a5);
        border-radius:20px;
        box-shadow:0 8px 24px rgba(16,39,70,0.16);
    ">
        <div style="
            font-size:42px;
            font-weight:800;
            color:#ffffff;
            letter-spacing:-1px;
        ">♥ CareFlow</div>
        <div style="
            color:#dbeafe;
            font-size:17px;
            font-weight:600;
            margin-top:8px;
        ">Clinical Pathway Process Mining</div>
        <div style="
            color:#ffffff;
            font-size:14px;
            margin-top:14px;
            line-height:1.6;
        ">Sign in to access your clinical analytics workspace.</div>
    </div>
    """,
    unsafe_allow_html=True
)
    login_tab, signup_tab = st.tabs(
        ["Login", "Create account"]
    )

    with login_tab:
        with st.form("careflow_login_form"):
            login_email = st.text_input("Email address")
            login_password = st.text_input(
                "Password", type="password"
            )
            login_submit = st.form_submit_button(
                "Login", use_container_width=True
            )

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
                st.error(
                    "Login failed. Check your email and password "
                    "or verify your email address."
                )

    with signup_tab:
        with st.form("careflow_signup_form"):
            signup_email = st.text_input("Email address")
            signup_password = st.text_input(
                "Create password", type="password"
            )
            confirm_password = st.text_input(
                "Confirm password", type="password"
            )
            signup_submit = st.form_submit_button(
                "Create account", use_container_width=True
            )

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
                        st.success(
                            "Registration received. Check your email "
                            "to verify your account, then log in."
                        )

                except Exception:
                    st.error(
                        "Signup failed. Check your email, password "
                        "requirements, and Supabase authentication settings."
                    )

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
.block-container{padding-top:1.2rem;max-width:1500px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#102746,#173c62)}
[data-testid="stSidebar"] *{color:#f7fbff}
[data-testid="stSidebar"] button {
    background: #245b8f !important;
    color: #ffffff !important;
    border: 1px solid #4b83b5 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] button:hover {
    background: #167d91 !important;
    border-color: #5eead4 !important;
}

/* Cleaner navigation spacing */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 6px;
}

[data-testid="stSidebar"] hr {
    border-color: #355574;
}
.hero{padding:1.4rem 1.6rem;border-radius:18px;background:linear-gradient(115deg,#102746,#2463a5);color:#fff;margin-bottom:1rem}
.hero h1{color:#fff;margin:0;font-size:2rem}.hero p{color:#dbeafe;margin:.35rem 0 0}
.metric-card{border:1px solid #e1e9f3;border-radius:14px;background:#fff;padding:16px;min-height:105px}
.metric-label{color:#64748b;font-size:.85rem}.metric-value{color:#102746;font-size:1.8rem;font-weight:750}
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
                "Dashboard",
                "Task Board",
                "Reports",
                "Care coordination",
                "Patient Flow",
                "Clinical Pathways",
                "Care Teams",
                "Governance",
                "Profile",
            ],
            key="careflow_workspace_menu",
            label_visibility="collapsed",
        )
        st.divider()
    st.caption("Clinical Pathway Process Mining")
    st.caption("Data source: " + source_name)
    synthetic_department = False
    if synthetic_department:
        st.caption("Department labels are synthetic demo assignments; the source file has no department field.")

st.markdown(f'<div class="hero"><h1>CareFlow <span style="font-weight:400;font-size:1.05rem">/ {page}</span></h1><p>Clinical Pathway Process Mining · Care coordination workspace</p></div>', unsafe_allow_html=True)

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

if page == "Dashboard":
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

elif page == "Task Board":
    st.subheader("☷ Task Board")
    st.caption("Sample coordination tasks are illustrative; no task is written back to a hospital system.")
    tasks = pd.DataFrame([
        {"Task":"Review delayed pathway","Department":"Emergency","Priority":"High","Assignee":"Care Team Alpha","Status":"Open"},
        {"Task":"Check missing event timestamp","Department":"Process Analytics","Priority":"Medium","Assignee":"Data Quality Team","Status":"In progress"},
        {"Task":"Confirm follow-up sequence","Department":"Care Coordination","Priority":"Medium","Assignee":"Care Team Beta","Status":"Open"},
        {"Task":"Review pathway deviation","Department":"Clinical Governance","Priority":"High","Assignee":"Pathway Lead","Status":"Review"},
    ])
    st.dataframe(tasks,use_container_width=True,hide_index=True)
    with st.form("task_form"):
        title=st.text_input("New task")
        dept=st.text_input("Department")
        priority=st.selectbox("Priority",["High","Medium","Low"])
        submitted=st.form_submit_button("Add demo task")
        if submitted:
            if title.strip(): st.success(f"Task captured for this session: {title} · {dept or 'Unassigned'} · {priority}")
            else: st.error("Enter a task name.")

elif page == "Reports":
    st.subheader("▥ Reports")
    st.write("Generate an overview from the uploaded event log.")
    a,b,c=st.columns(3)
    a.metric("Event records",f"{n_events:,}")
    b.metric("Cases / patients",f"{n_cases:,}")
    c.metric("Activities",f"{n_activities:,}" if activity_col else "Not detected")
    st.dataframe(filtered.describe(include="all").transpose().reset_index(names="Field"),use_container_width=True)
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

elif page == "Governance":
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


elif page == "Profile":
    st.subheader("👨‍⚕️ Doctor Profile")
    st.caption("Professional information and account details")

    user = st.session_state.careflow_user
    email = user.get("email", "")

    with st.form("doctor_profile_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)

        with col1:
            doctor_name = st.text_input("Doctor Name")
            age = st.number_input(
                "Age", min_value=18, max_value=100, value=30
            )
            gender = st.selectbox(
                "Gender",
                ["Prefer not to say", "Female", "Male", "Other"]
            )

        with col2:
            department = st.selectbox(
                "Department",
                [
                    "General Medicine", "Emergency", "Cardiology",
                    "Neurology", "Paediatrics", "Orthopaedics",
                    "Surgery", "Other"
                ]
            )
            designation = st.selectbox(
                "Designation",
                [
                    "Doctor", "Resident Doctor", "Consultant",
                    "Senior Consultant", "Department Head", "Other"
                ]
            )
            employee_id = st.text_input("Employee ID (optional)")

        st.markdown("### Contact Information")
        st.text_input("Account Email", value=email, disabled=True)
        contact_no = st.text_input("Contact Number")
        hospital = st.text_input("Hospital / Healthcare Facility")
        location = st.text_input("City / Location")

        st.markdown("### Professional Information")
        qualification = st.text_input("Medical Qualification")
        specialization = st.text_input("Specialization")
        experience = st.number_input(
            "Years of Experience", min_value=0, max_value=70, value=0
        )
        bio = st.text_area("Professional Bio")

        submitted = st.form_submit_button(
            "Save Profile", use_container_width=True
        )

    if submitted:
        st.session_state["careflow_doctor_profile"] = {
            "Doctor Name": doctor_name,
            "Age": age,
            "Gender": gender,
            "Department": department,
            "Designation": designation,
            "Employee ID": employee_id,
            "Email": email,
            "Contact Number": contact_no,
            "Hospital": hospital,
            "Location": location,
            "Qualification": qualification,
            "Specialization": specialization,
            "Experience": experience,
            "Bio": bio,
        }
        st.success("Profile saved for this session.")
        st.info(
            "Profile details are temporary and will not persist "
            "after the session ends. Permanent storage is not "
            "configured yet."
        )
st.divider()
st.caption("CareFlow is a process-mining demonstration, not a clinical decision-support system. Department labels are synthetic where indicated. Do not publish identifiable patient or health data to a public repository.")
