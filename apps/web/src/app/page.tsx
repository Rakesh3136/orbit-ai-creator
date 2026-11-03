"use client";

import {
  Activity,
  Bot,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clapperboard,
  Command,
  Film,
  Globe2,
  LayoutDashboard,
  MessageSquare,
  Plus,
  Radio,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Youtube,
} from "lucide-react";

const navigation = [
  { label: "Overview", icon: LayoutDashboard, active: true },
  { label: "AI CEO", icon: MessageSquare },
  { label: "Channels", icon: Youtube },
  { label: "Agent workforce", icon: Bot },
  { label: "Content studio", icon: Clapperboard },
  { label: "Publishing", icon: Radio },
  { label: "Analytics", icon: Activity },
  { label: "Approvals", icon: ShieldCheck },
];

const departments = [
  ["01", "Research & intelligence", "Discover niches, trends and audiences"],
  ["02", "Channel strategy", "Build a distinct plan for every channel"],
  ["03", "Editorial & scripts", "Turn evidence into original stories"],
  ["04", "Creative production", "Images, voice, video and 3D workflows"],
  ["05", "Growth & analytics", "Measure results and run experiments"],
  ["06", "Publishing & community", "Prepare uploads and audience responses"],
];

export default function Home() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Command size={19} /></div>
          <div><strong>AIMN</strong><span>MEDIA NETWORK OS</span></div>
        </div>
        <div className="workspace-switcher">
          <div className="workspace-avatar">M</div>
          <div className="workspace-copy"><strong>My media network</strong><span>Owner workspace</span></div>
          <ChevronDown size={15} />
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav className="nav-list">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <a className={item.active ? "nav-item active" : "nav-item"} href="#" key={item.label}>
                <Icon size={17} strokeWidth={1.8} />
                <span>{item.label}</span>
                {item.label === "Approvals" && <span className="nav-count">0</span>}
              </a>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <a className="nav-item" href="#"><Settings2 size={17} /><span>Settings</span></a>
          <a className="nav-item" href="#"><CircleHelp size={17} /><span>Help & documentation</span></a>
          <div className="owner-card"><div className="owner-avatar">O</div><div><strong>Network owner</strong><span>Full access</span></div><span className="online-dot" /></div>
        </div>
      </aside>

      <section className="main-area">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> <strong>Overview</strong></div>
          <div className="top-actions"><div className="search-box"><Search size={15} /><span>Search network</span><kbd>⌘ K</kbd></div><button className="icon-button" aria-label="Activity"><Activity size={17} /></button><div className="profile-dot">O</div></div>
        </header>

        <div className="page-content">
          <div className="welcome-row">
            <div><div className="eyebrow"><Sparkles size={13} /> YOUR AI-OPERATED MEDIA BUSINESS</div><h1>Command center</h1><p>One intelligence layer. Multiple channels. A coordinated creative workforce.</p></div>
            <button className="primary-button" disabled title="Channel setup will be enabled after the channel service is connected"><Plus size={16} /> New channel <span className="soon-tag">SOON</span></button>
          </div>

          <section className="status-banner">
            <div className="status-icon"><Activity size={19} /></div>
            <div className="status-copy"><strong>Foundation workspace</strong><span>The interface is in place. Backend services, secure sign-in and live agent execution are the next build steps.</span></div>
            <span className="status-pill">IN DEVELOPMENT</span>
          </section>

          <section className="metric-grid" aria-label="Network metrics">
            {[["Channels", "—", "Connect a YouTube channel"], ["Active agents", "—", "Agent runtime not connected"], ["Tasks in progress", "—", "Workflow engine not connected"], ["Approvals waiting", "—", "Approval service not connected"]].map(([label, value, note]) => (
              <article className="metric-card" key={label}><span>{label}</span><strong>{value}</strong><small>{note}</small></article>
            ))}
          </section>

          <div className="content-grid">
            <section className="panel ai-panel">
              <div className="panel-heading"><div className="panel-icon violet"><Sparkles size={17} /></div><div><h2>Talk to your AI CEO</h2><p>Your single point of contact for the entire network.</p></div><span className="coming-label">CONNECTING NEXT</span></div>
              <div className="chat-empty"><div className="chat-orb"><Bot size={27} /></div><h3>Your AI CEO will work here</h3><p>Ask for research, channel strategies, production plans or a network-wide performance review. The CEO will delegate work to specialist agents and report back here.</p><div className="suggestion-list"><span><Globe2 size={14} /> Find promising global niches</span><span><Youtube size={14} /> Prepare a channel launch plan</span><span><Film size={14} /> Plan the next video production</span></div></div>
              <div className="chat-composer"><span>AI CEO chat becomes available after backend integration</span><button disabled aria-label="Send message"><MessageSquare size={16} /></button></div>
            </section>

            <section className="panel departments-panel">
              <div className="panel-heading"><div className="panel-icon blue"><Bot size={17} /></div><div><h2>Agent departments</h2><p>Specialist teams coordinated by the CEO.</p></div></div>
              <div className="department-list">{departments.map(([number, title, description]) => <div className="department-row" key={number}><span className="department-number">{number}</span><div><strong>{title}</strong><small>{description}</small></div><span className="department-state">PLANNED</span></div>)}</div>
            </section>
          </div>

          <section className="panel bottom-panel"><div className="panel-heading"><div className="panel-icon green"><CheckCircle2 size={17} /></div><div><h2>Build priorities</h2><p>What must be connected before the network can operate.</p></div></div><div className="priority-grid"><div><span className="priority-index">01</span><strong>Secure platform foundation</strong><small>Authentication, database, API and tenant isolation</small></div><div><span className="priority-index">02</span><strong>AI CEO & agent runtime</strong><small>Task orchestration, memory and live status</small></div><div><span className="priority-index">03</span><strong>Channel operations</strong><small>YouTube OAuth, workflows and approval controls</small></div></div></section>
          <footer><span>AIMN · Autonomous AI Media Network</span><span><ShieldCheck size={13} /> Human-governed external actions</span></footer>
        </div>
      </section>
    </main>
  );
}
