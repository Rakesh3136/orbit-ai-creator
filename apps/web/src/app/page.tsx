"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { Activity, Bot, CheckCircle2, Command, LogOut, Plus, RefreshCw, ShieldCheck, Youtube } from "lucide-react";

const API = (process.env.NEXT_PUBLIC_AIMN_API_URL || "http://localhost:8000").replace(/\/$/, "");
type Network = { id: string; name: string; default_locale: string; status: string };
type Channel = { id: string; name: string; slug: string; niche?: string | null; status: string; connected: boolean };
type Agent = { id: string; name: string; department: string; description: string };
type Task = { id: string; title: string; agent_id: string; status: string; external_action: boolean };
type Approval = { id: string; task_id: string; status: string; decision_note?: string | null };

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [owner, setOwner] = useState("");
  const [authenticated, setAuthenticated] = useState(false);
  const [networks, setNetworks] = useState<Network[]>([]);
  const [networkId, setNetworkId] = useState("");
  const [channels, setChannels] = useState<Channel[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [networkName, setNetworkName] = useState("My media network");
  const [channelName, setChannelName] = useState("");
  const [channelNiche, setChannelNiche] = useState("");
  const [taskTitle, setTaskTitle] = useState("");
  const [taskInstruction, setTaskInstruction] = useState("");
  const [taskAgent, setTaskAgent] = useState("research");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const refresh = useCallback(async (selectedId?: string) => {
    const [networkData, agentData] = await Promise.all([
      request<Network[]>("/api/v1/networks"),
      request<Agent[]>("/api/v1/agents"),
    ]);
    setNetworks(networkData);
    setAgents(agentData);
    const id = selectedId || networkId || networkData[0]?.id || "";
    setNetworkId(id);
    if (id) {
      const [channelData, taskData, approvalData] = await Promise.all([
        request<Channel[]>(`/api/v1/networks/${id}/channels`),
        request<Task[]>(`/api/v1/networks/${id}/tasks`),
        request<Approval[]>(`/api/v1/networks/${id}/approvals?status=pending`),
      ]);
      setChannels(channelData);
      setTasks(taskData);
      setApprovals(approvalData);
    } else {
      setChannels([]); setTasks([]); setApprovals([]);
    }
  }, [networkId]);

  useEffect(() => {
    request<{ authenticated: boolean; email: string }>("/api/v1/auth/me")
      .then((data) => { setOwner(data.email); setAuthenticated(true); })
      .catch(() => setAuthenticated(false));
  }, []);

  useEffect(() => {
    if (authenticated) refresh().catch((e) => setError(e.message));
  }, [authenticated, refresh]);

  async function run(action: () => Promise<void>) {
    setBusy(true); setError(""); setNotice("");
    try { await action(); } catch (e) { setError(e instanceof Error ? e.message : "Something went wrong"); }
    finally { setBusy(false); }
  }

  async function login(event: FormEvent) {
    event.preventDefault();
    await run(async () => {
      const result = await request<{ email: string }>("/api/v1/auth/login", {
        method: "POST", body: JSON.stringify({ email, password }),
      });
      setOwner(result.email); setPassword(""); setAuthenticated(true);
      setNotice("Signed in securely.");
    });
  }

  async function logout() {
    await run(async () => {
      await request("/api/v1/auth/logout", { method: "POST" });
      setAuthenticated(false); setOwner(""); setNetworks([]); setChannels([]); setTasks([]); setApprovals([]);
    });
  }

  async function createNetwork(event: FormEvent) {
    event.preventDefault();
    await run(async () => {
      const created = await request<Network>("/api/v1/networks", {
        method: "POST", body: JSON.stringify({ name: networkName, default_locale: "en" }),
      });
      await refresh(created.id);
      setNotice("Network created.");
    });
  }

  async function createChannel(event: FormEvent) {
    event.preventDefault();
    if (!networkId) return;
    const slug = channelName.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    await run(async () => {
      await request(`/api/v1/networks/${networkId}/channels`, {
        method: "POST", body: JSON.stringify({ name: channelName, slug, niche: channelNiche || null }),
      });
      setChannelName(""); setChannelNiche(""); await refresh(networkId); setNotice("Channel added as a draft.");
    });
  }

  async function createTask(event: FormEvent) {
    event.preventDefault();
    if (!networkId) return;
    await run(async () => {
      await request(`/api/v1/networks/${networkId}/tasks`, {
        method: "POST", body: JSON.stringify({ agent_id: taskAgent, title: taskTitle, instruction: taskInstruction, external_action: false }),
      });
      setTaskTitle(""); setTaskInstruction(""); await refresh(networkId); setNotice("Task queued. Worker execution is not enabled yet.");
    });
  }

  async function decide(id: string, decision: "approved" | "rejected") {
    await run(async () => {
      await request(`/api/v1/approvals/${id}/decision`, {
        method: "POST", body: JSON.stringify({ decision, note: "Decision made by network owner in AIMN dashboard." }),
      });
      await refresh(networkId); setNotice(`Approval ${decision}.`);
    });
  }

  if (!authenticated) return (
    <main className="auth-screen">
      <form className="login-card" onSubmit={login}>
        <div className="login-brand"><span><Command size={22} /></span><div><b>AIMN</b><small>MEDIA NETWORK OS</small></div></div>
        <p className="eyebrow">OWNER ACCESS</p><h1>Welcome back</h1>
        <p className="login-description">Sign in to manage your AI media network.</p>
        <label>Email address<input type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>Password<input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        {error && <p className="error-message">{error}</p>}
        <button className="primary-button login-button" disabled={busy}>{busy ? "Signing in…" : "Sign in securely"}</button>
        <p className="security-note"><ShieldCheck size={14} /> Protected by an HttpOnly owner session.</p>
        <p className="api-hint">API: {API}</p>
      </form>
    </main>
  );

  return (
    <main className="dashboard">
      <aside className="side-nav">
        <div className="login-brand"><span><Command size={20} /></span><div><b>AIMN</b><small>MEDIA NETWORK OS</small></div></div>
        <p className="side-label">WORKSPACE</p>
        <div className="side-link active"><Activity size={17} /> Overview</div>
        <div className="side-link"><Youtube size={17} /> Channels</div>
        <div className="side-link"><Bot size={17} /> Agent workforce</div>
        <div className="side-link"><ShieldCheck size={17} /> Approvals <b className="count">{approvals.length}</b></div>
        <div className="side-owner"><span className="avatar">O</span><div><b>{owner}</b><small>Network owner</small></div><button onClick={logout} title="Sign out"><LogOut size={16} /></button></div>
      </aside>
      <section className="workspace">
        <header className="topbar"><span>Workspace / <b>Command center</b></span><button className="refresh-button" onClick={() => run(() => refresh())} disabled={busy}><RefreshCw size={15} /> Refresh</button></header>
        <div className="page">
          <div className="page-title"><div><p className="eyebrow">YOUR AI-OPERATED MEDIA BUSINESS</p><h1>Command center</h1><p>Live data from your AIMN backend. External actions remain approval-gated.</p></div></div>
          {error && <div className="alert error-message">{error}</div>}
          {notice && <div className="alert success-message">{notice}</div>}
          <section className="metric-grid">
            <article><small>Networks</small><strong>{networks.length}</strong></article>
            <article><small>Channels</small><strong>{channels.length}</strong></article>
            <article><small>Agent tasks</small><strong>{tasks.length}</strong></article>
            <article><small>Pending approvals</small><strong>{approvals.length}</strong></article>
          </section>
          <section className="panel network-panel">
            <div className="section-heading"><div><h2>Media network</h2><p>Select a workspace or create your first one.</p></div></div>
            {networks.length > 0 ? <select value={networkId} onChange={(e) => run(() => refresh(e.target.value))}>{networks.map((n) => <option key={n.id} value={n.id}>{n.name}</option>)}</select> :
              <form className="inline-form" onSubmit={createNetwork}><input value={networkName} onChange={(e) => setNetworkName(e.target.value)} aria-label="Network name" required minLength={2} /><button className="primary-button" disabled={busy}><Plus size={15} /> Create network</button></form>}
          </section>
          <div className="columns">
            <section className="panel"><div className="section-heading"><div><h2>YouTube channels</h2><p>Channels in the selected network.</p></div></div>
              {channels.length ? <div className="data-list">{channels.map((c) => <div className="data-row" key={c.id}><div><b>{c.name}</b><small>{c.niche || c.slug}</small></div><span className={c.connected ? "tag connected" : "tag"}>{c.connected ? "CONNECTED" : c.status.toUpperCase()}</span></div>)}</div> : <p className="empty-state">No channels yet. Add your first channel profile below.</p>}
              {networkId && <form className="stack-form" onSubmit={createChannel}><input placeholder="Channel name" value={channelName} onChange={(e) => setChannelName(e.target.value)} required minLength={2} /><input placeholder="Niche (optional)" value={channelNiche} onChange={(e) => setChannelNiche(e.target.value)} /><button className="secondary-button" disabled={busy}><Plus size={14} /> Add channel profile</button></form>}
            </section>
            <section className="panel"><div className="section-heading"><div><h2>Agent workforce</h2><p>Available specialist roles.</p></div></div>
              <div className="data-list">{agents.map((a) => <div className="data-row" key={a.id}><div><b>{a.name}</b><small>{a.description}</small></div><span className="tag">READY</span></div>)}</div>
            </section>
          </div>
          <div className="columns">
            <section className="panel"><div className="section-heading"><div><h2>Task queue</h2><p>Tasks are recorded; a worker process is the next milestone.</p></div></div>
              {tasks.length ? <div className="data-list">{tasks.map((t) => <div className="data-row" key={t.id}><div><b>{t.title}</b><small>{t.agent_id}</small></div><span className="tag">{t.status.toUpperCase()}</span></div>)}</div> : <p className="empty-state">No tasks queued yet.</p>}
              {networkId && <form className="stack-form" onSubmit={createTask}><input placeholder="Task title" value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} required minLength={3} /><select value={taskAgent} onChange={(e) => setTaskAgent(e.target.value)}>{agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</select><textarea placeholder="Describe the research or work to perform…" value={taskInstruction} onChange={(e) => setTaskInstruction(e.target.value)} required minLength={5} /><button className="secondary-button" disabled={busy || !agents.length}><Plus size={14} /> Queue task</button></form>}
            </section>
            <section className="panel"><div className="section-heading"><div><h2>Approval center</h2><p>Owner decisions for external actions.</p></div></div>
              {approvals.length ? <div className="data-list">{approvals.map((a) => <div className="approval-row" key={a.id}><small>Task {a.task_id.slice(0, 8)}…</small><div><button className="approve-button" disabled={busy} onClick={() => decide(a.id, "approved")}>Approve</button><button className="reject-button" disabled={busy} onClick={() => decide(a.id, "rejected")}>Reject</button></div></div>)}</div> : <p className="empty-state"><CheckCircle2 size={17} /> No pending approvals.</p>}
            </section>
          </div>
          <footer><span>AIMN · Autonomous AI Media Network</span><span><ShieldCheck size={13} /> Human approval required for external actions</span></footer>
        </div>
      </section>
    </main>
  );
}
