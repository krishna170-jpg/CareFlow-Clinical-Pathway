
import { useEffect, useMemo, useState } from "react";
import Papa from "papaparse";
import {
  Activity, BarChart3, ShieldCheck, GitBranch, Users,
  ClipboardList, FileText, Upload, LogOut, Menu, X,
  Clock3, CheckCircle2, AlertCircle, LockKeyhole
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, CartesianGrid
} from "recharts";
import { supabase } from "./supabaseClient";

const sections = [
  { name: "Overview", icon: BarChart3 },
  { name: "Patient Flow", icon: Activity },
  { name: "Clinical Pathways", icon: GitBranch },
  { name: "Task Board", icon: ClipboardList },
  { name: "Reports", icon: FileText },
  { name: "Care Teams", icon: Users },
  { name: "Governance", icon: ShieldCheck }
];

const normal = value =>
  String(value ?? "").trim().toLowerCase().replace(/[\s_-]+/g, "");

function findColumn(headers, choices) {
  return headers.find(h => choices.includes(normal(h)));
}

export default function App() {
  const [section, setSection] = useState("Overview");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [session, setSession] = useState(null);
  const [authMode, setAuthMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [rows, setRows] = useState([]);
  const [fileName, setFileName] = useState("");
  const [caseColumn, setCaseColumn] = useState("");
  const [activityColumn, setActivityColumn] = useState("");
  const [timeColumn, setTimeColumn] = useState("");

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s);
    });
    return () => data.subscription.unsubscribe();
  }, []);

  async function authenticate(e) {
    e.preventDefault();
    if (!supabase) {
      setMessage("Supabase is not configured yet. Set the Vercel environment variables.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const result = authMode === "login"
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });
      if (result.error) throw result.error;
      if (authMode === "signup" && !result.data.session) {
        setMessage("Account created. Check your email to confirm registration.");
      }
    } catch (err) {
      setMessage(err.message || "Authentication failed.");
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    if (supabase) await supabase.auth.signOut();
    setSession(null);
  }

  function loadCSV(file) {
    if (!file) return;
    setMessage("");
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: result => {
        const data = result.data.filter(row =>
          Object.values(row).some(v => String(v ?? "").trim())
        );
        const headers = result.meta.fields || [];
        const c = findColumn(headers, [
          "caseid", "case", "patientid", "encounterid", "visitid", "processid"
        ]);
        const a = findColumn(headers, [
          "activity", "event", "eventname", "activityname", "eventtype"
        ]);
        const t = findColumn(headers, [
          "timestamp", "eventtime", "datetime", "eventtimestamp", "time"
        ]);
        setRows(data);
        setFileName(file.name);
        setCaseColumn(c || "");
        setActivityColumn(a || "");
        setTimeColumn(t || "");
        if (!c || !a) {
          setMessage("CSV loaded, but case ID or activity column was not detected. Check your column names.");
        }
      },
      error: err => setMessage(err.message || "Unable to read CSV.")
    });
  }

  const metrics = useMemo(() => {
    const cases = caseColumn
      ? new Set(rows.map(r => String(r[caseColumn] ?? "").trim()).filter(Boolean)).size
      : 0;
    const activities = activityColumn
      ? new Set(rows.map(r => String(r[activityColumn] ?? "").trim()).filter(Boolean)).size
      : 0;
    const counts = {};
    rows.forEach(r => {
      const value = String(r[activityColumn] ?? "").trim();
      if (value) counts[value] = (counts[value] || 0) + 1;
    });
    const chart = Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
    let duration = null;
    if (caseColumn && timeColumn) {
      const times = new Map();
      rows.forEach(r => {
        const id = String(r[caseColumn] ?? "").trim();
        const date = Date.parse(r[timeColumn]);
        if (!id || !Number.isFinite(date)) return;
        const old = times.get(id) || [date, date];
        times.set(id, [Math.min(old[0], date), Math.max(old[1], date)]);
      });
      const values = [...times.values()].map(([a, b]) => (b - a) / 3600000);
      if (values.length) {
        values.sort((a, b) => a - b);
        duration = values[Math.floor(values.length / 2)];
      }
    }
    return { cases, activities, chart, duration };
  }, [rows, caseColumn, activityColumn, timeColumn]);

  const hasData = rows.length > 0;
  const authenticated = Boolean(session);

  if (!authenticated) {
    return (
      <main className="auth-page">
        <section className="auth-brand">
          <div className="brand-mark"><Activity size={27}/></div>
          <div>
            <h1>CareFlow</h1>
            <p>Clinical Pathway Process Mining</p>
          </div>
        </section>
        <section className="auth-card">
          <span className="eyebrow">CLINICAL INTELLIGENCE PLATFORM</span>
          <h2>{authMode === "login" ? "Welcome back" : "Create your account"}</h2>
          <p className="muted">Sign in to access your CareFlow workspace.</p>
          <form onSubmit={authenticate}>
            <label>Email address</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="you@example.com"/>
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} placeholder="At least 6 characters"/>
            <button className="primary full" disabled={busy}>
              {busy ? "Please wait..." : authMode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>
          <button className="text-button" onClick={() => {
            setAuthMode(authMode === "login" ? "signup" : "login");
            setMessage("");
          }}>
            {authMode === "login" ? "New to CareFlow? Create an account" : "Already registered? Sign in"}
          </button>
          {!supabase && <p className="notice"><LockKeyhole size={16}/> Configure Supabase in hosting settings to enable login.</p>}
          {message && <p className="notice">{message}</p>}
        </section>
        <p className="auth-foot">Secure access • Clinical operations analytics</p>
      </main>
    );
  }

  return (
    <div className="app-shell">
      {mobileMenu && <button className="scrim" onClick={() => setMobileMenu(false)} aria-label="Close menu"/>}
      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><Activity size={24}/></div>
          <div><strong>CareFlow</strong><small>CLINICAL INTELLIGENCE</small></div>
          <button className="icon-button mobile-close" onClick={() => setMobileMenu(false)}><X/></button>
        </div>
        <div className="workspace-label">WORKSPACE</div>
        <nav>
          {sections.map(item => {
            const Icon = item.icon;
            return <button key={item.name}
              className={`nav-item ${section === item.name ? "active" : ""}`}
              onClick={() => { setSection(item.name); setMobileMenu(false); }}>
              <Icon size={18}/><span>{item.name}</span>
            </button>;
          })}
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck size={18}/>
          <div><strong>Workspace security</strong><small>Authenticated session</small></div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button className="icon-button menu-toggle" onClick={() => setMobileMenu(true)}><Menu/></button>
          <div><span className="breadcrumb">CareFlow /</span> <strong>{section}</strong></div>
          <div className="user-area">
            <span className="status-dot"/> <span className="user-email">{session.user.email}</span>
            <button className="icon-button" onClick={logout} title="Sign out"><LogOut size={18}/></button>
          </div>
        </header>

        <div className="content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">CARE OPERATIONS PLATFORM</span>
              <h1>{section === "Overview" ? "Clinical operations overview" : section}</h1>
              <p className="muted">Understand care delivery through your event-log data.</p>
            </div>
            <label className="upload-button">
              <Upload size={17}/> Upload event log
              <input type="file" accept=".csv,text/csv" onChange={e => loadCSV(e.target.files?.[0])}/>
            </label>
          </div>

          {message && <div className="notice"><AlertCircle size={17}/>{message}</div>}

          {!hasData && <div className="upload-panel">
            <div className="upload-icon"><Upload size={25}/></div>
            <div><h3>Connect your actual event log</h3>
              <p className="muted">Upload a CSV containing case identifiers, activities and, if available, event timestamps. Analysis runs in this browser.</p>
            </div>
            <label className="secondary-button">Choose CSV
              <input type="file" accept=".csv,text/csv" onChange={e => loadCSV(e.target.files?.[0])}/>
            </label>
          </div>}

          {hasData && <div className="file-banner">
            <CheckCircle2 size={18}/> <span><strong>{fileName}</strong> · {rows.length.toLocaleString()} event rows loaded</span>
            <button className="text-button" onClick={() => {setRows([]);setFileName("");setMessage("");}}>Remove</button>
          </div>}

          {section === "Governance" && <div className="panel">
            <h3><ShieldCheck size={19}/> Governance and data controls</h3>
            <p>Sign-in is provided by Supabase. This prototype analyses the uploaded CSV locally in your browser and does not save it to the database.</p>
            <p className="muted">Before production use, configure database row-level security, role permissions, retention rules and audit logging.</p>
          </div>}

          {section === "Task Board" && <div className="panel">
            <h3><ClipboardList size={20}/> Task Board</h3>
            <p className="muted">No tasks have been connected yet. Shared tasks require a secured database table and access policies.</p>
          </div>}

          {section === "Care Teams" && <div className="panel">
            <h3><Users size={20}/> Care Teams</h3>
            <p className="muted">Team management will become available after team membership and role permissions are configured.</p>
          </div>}

          {section === "Reports" && <div className="panel">
            <h3><FileText size={20}/> Event-log report</h3>
            <p className="muted">Download a summary of the analytics currently calculated from your uploaded file.</p>
            <button className="secondary-button" disabled={!hasData} onClick={() => {
              const blob = new Blob([JSON.stringify({fileName, rows: rows.length, metrics}, null, 2)], {type:"application/json"});
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url; a.download = "careflow-report.json"; a.click();
              URL.revokeObjectURL(url);
            }}>Export report (JSON)</button>
          </div>}

          {section === "Clinical Pathways" && <div className="panel">
            <h3><GitBranch size={20}/> Clinical pathway analysis</h3>
            <p className="muted">Pathway sequences will be calculated from the detected case ID, activity and timestamp columns. Check your uploaded file's column names if these are not detected automatically.</p>
            {hasData && caseColumn && activityColumn && <div className="table-wrap"><table>
              <thead><tr><th>Case ID</th><th>Event count</th><th>Activity sequence</th></tr></thead>
              <tbody>{Object.entries(rows.reduce((acc, r) => {
                const id = String(r[caseColumn] ?? "").trim();
                if (!id) return acc;
                if (!acc[id]) acc[id] = [];
                acc[id].push(r);
                return acc;
              }, {})).slice(0, 12).map(([id, events]) => {
                const ordered = timeColumn ? [...events].sort((a,b) => Date.parse(a[timeColumn]) - Date.parse(b[timeColumn])) : events;
                return <tr key={id}><td>{id}</td><td>{events.length}</td><td>{ordered.map(e => e[activityColumn]).filter(Boolean).join(" → ")}</td></tr>;
              })}</tbody>
            </table></div>}
          </div>}

          {section === "Patient Flow" && <div className="panel">
            <h3><Activity size={20}/> Patient flow</h3>
            <p className="muted">Activity counts below are calculated from your uploaded event log, not example data.</p>
            {hasData && metrics.chart.length > 0 && <div className="chart-box"><ResponsiveContainer width="100%" height={320}>
              <BarChart data={metrics.chart} margin={{top:10,right:15,left:0,bottom:45}}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e7edf3"/>
                <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} height={75} tick={{fontSize:11}}/>
                <YAxis/><Tooltip/><Bar dataKey="count" fill="#148b83" radius={[5,5,0,0]}/>
              </BarChart>
            </ResponsiveContainer></div>}
          </div>}

          {section === "Overview" && <>
            <div className="metric-grid">
              <Metric icon={Users} label="Unique cases" value={hasData && caseColumn ? metrics.cases.toLocaleString() : "—"} hint={caseColumn ? "From event log" : "Case ID column needed"}/>
              <Metric icon={Activity} label="Event records" value={hasData ? rows.length.toLocaleString() : "—"} hint="Rows in uploaded CSV"/>
              <Metric icon={GitBranch} label="Distinct activities" value={hasData && activityColumn ? metrics.activities : "—"} hint={activityColumn ? "Activity types found" : "Activity column needed"}/>
              <Metric icon={Clock3} label="Median case duration" value={metrics.duration == null ? "—" : `${metrics.duration.toFixed(2)} h`} hint={timeColumn ? "Calculated from timestamps" : "Timestamp column needed"}/>
            </div>
            <div className="panel">
              <div className="panel-title"><div><h3>Activity distribution</h3><p className="muted">Most frequent activities in the uploaded event log</p></div><Activity size={20}/></div>
              {!hasData ? <div className="empty-state"><BarChart3 size={32}/><strong>Analytics waiting for your data</strong><p>Upload your actual event-log CSV to calculate metrics and charts.</p></div>
              : metrics.chart.length ? <div className="chart-box"><ResponsiveContainer width="100%" height={320}>
                <BarChart data={metrics.chart} margin={{top:10,right:15,left:0,bottom:45}}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e7edf3"/>
                  <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} height={75} tick={{fontSize:11}}/>
                  <YAxis/><Tooltip/><Bar dataKey="count" fill="#148b83" radius={[5,5,0,0]}/>
                </BarChart>
              </ResponsiveContainer></div> : <p className="muted">Activity column not detected.</p>}
            </div>
            {hasData && <div className="panel">
              <h3>Detected CSV columns</h3>
              <div className="column-grid">
                <Column label="Case ID" value={caseColumn}/>
                <Column label="Activity" value={activityColumn}/>
                <Column label="Timestamp" value={timeColumn}/>
              </div>
              <p className="muted">If a field is blank, check whether your CSV uses a different column name.</p>
            </div>}
          </>}

          {section !== "Overview" && section !== "Patient Flow" && section !== "Clinical Pathways" && section !== "Task Board" && section !== "Reports" && section !== "Care Teams" && section !== "Governance" && <p>Section unavailable.</p>}

          <footer>CareFlow · Clinical Pathway Process Mining <span>Secure analytics workspace</span></footer>
        </div>
      </main>
    </div>
  );
}

function Metric({icon: Icon, label, value, hint}) {
  return <div className="metric-card"><div className="metric-top"><span>{label}</span><Icon size={19}/></div><strong className="metric-value">{value}</strong><span className="metric-hint">{hint}</span></div>;
}
function Column({label, value}) {
  return <div className="column-item"><span>{label}</span><strong>{value || "Not detected"}</strong></div>;
          }
            
