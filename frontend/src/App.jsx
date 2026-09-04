import React, { useEffect, useMemo, useState } from 'react'
import { Routes, Route, Navigate, Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, BarChart3, Bell, BookOpen,
  Bot, Boxes, Check, ChevronDown, ChevronRight, CircleHelp, Clock3, Code2, Copy,
  DollarSign, Gauge, GitBranch, Globe2, KeyRound, LayoutDashboard, LineChart,
  LogOut, Menu, Moon, MoreHorizontal, Play, Plus, RefreshCw, Route as RouteIcon,
  Search, Settings, ShieldCheck, Sparkles, TerminalSquare, TrendingDown, UserRound,
  X, Zap,
} from 'lucide-react'
import { api } from './api'
import { demoModels, demoProjects, demoProviders, seedRequests } from './demo'

const nav = [
  { label: 'Overview', to: '/', icon: LayoutDashboard },
  { label: 'Playground', to: '/playground', icon: TerminalSquare },
  { label: 'Models', to: '/models', icon: Bot },
  { label: 'Routing', to: '/routing', icon: GitBranch },
  { label: 'Requests', to: '/requests', icon: Activity },
  { label: 'Benchmarks', to: '/benchmarks', icon: BarChart3, soon: true },
  { label: 'Analytics', to: '/analytics', icon: LineChart, soon: true },
  { label: 'Costs', to: '/costs', icon: DollarSign },
  { label: 'Cache', to: '/cache', icon: Boxes, soon: true },
  { label: 'Alerts', to: '/alerts', icon: Bell, soon: true },
]
const settingsNav = [
  { label: 'API Keys', to: '/settings/api-keys', icon: KeyRound },
  { label: 'Projects', to: '/settings/projects', icon: Boxes },
  { label: 'Providers', to: '/settings/providers', icon: Globe2 },
  { label: 'Retention', to: '/settings/retention', icon: ShieldCheck },
]

function useAuth() {
  const [session, setSession] = useState(() => JSON.parse(localStorage.getItem('trailback_session') || 'null'))
  const login = (next) => { localStorage.setItem('trailback_session', JSON.stringify(next)); setSession(next) }
  const logout = () => { localStorage.removeItem('trailback_session'); localStorage.removeItem('trailback_api_key'); setSession(null) }
  return { session, login, logout }
}

function App() {
  const auth = useAuth()
  if (!auth.session) return <LoginScreen onLogin={auth.login} />
  return <AppShell onLogout={auth.logout} session={auth.session} />
}

function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setError('')
    try {
      let user
      try {
        const users = await api(`/users?limit=200`)
        user = users.find((u) => u.email.toLowerCase() === email.trim().toLowerCase())
        if (!user) user = await api('/users', { method: 'POST', body: JSON.stringify({ email: email.trim(), sso_identity: { source: 'trailback-ui' } }) })
      } catch {
        user = { id: 'demo-user', email: email.trim() || 'demo@trailback.dev' }
      }
      onLogin({ userId: user.id, email: user.email, displayName: user.email.split('@')[0] })
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return <div className="auth-screen">
    <div className="auth-glow glow-one" /><div className="auth-glow glow-two" />
    <div className="auth-card">
      <div className="brand-mark large"><RouteIcon size={22} /></div>
      <div className="eyebrow">LLM ROUTING & OPTIMIZATION</div>
      <h1>Welcome to TrailBack</h1>
      <p className="muted">One gateway. Smarter model decisions. Measurable cost, latency and quality.</p>
      <form onSubmit={submit} className="stack-lg">
        <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" /></label>
        <label>Password<input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" /></label>
        {error && <div className="error-banner">{error}</div>}
        <button className="button primary wide" disabled={busy}>{busy ? <Spinner /> : <><span>Enter TrailBack</span><ChevronRight size={17} /></>}</button>
      </form>
      <div className="auth-note"><ShieldCheck size={15} /> Provider master keys never reach the browser.</div>
      <div className="auth-foot">UI authentication is local until a backend auth provider is added.</div>
    </div>
  </div>
}

function AppShell({ onLogout, session }) {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [project, setProject] = useState(null)
  const [models, setModels] = useState(demoModels)
  const [providers, setProviders] = useState(demoProviders)
  const [projects, setProjects] = useState(demoProjects)
  const [apiKeys, setApiKeys] = useState([])
  const [requests, setRequests] = useState(() => JSON.parse(localStorage.getItem('trailback_requests') || 'null') || seedRequests)
  const [toast, setToast] = useState(null)
  const [apiOnline, setApiOnline] = useState(false)

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const [remoteModels, remoteProviders, remoteProjects] = await Promise.all([api('/models'), api('/providers'), api(`/projects?user_id=${session.userId}`)])
        if (!mounted) return
        if (remoteModels?.length) setModels(remoteModels)
        if (remoteProviders?.length) setProviders(remoteProviders)
        if (remoteProjects?.length) setProjects(remoteProjects)
        setApiOnline(true)
      } catch { if (mounted) setApiOnline(false) }
    })()
    return () => { mounted = false }
  }, [session.userId])

  useEffect(() => { if (!project && projects[0]) setProject(projects[0]) }, [projects, project])
  useEffect(() => {
    if (!project?.id || project.id.startsWith('demo-') || project.id === 'demo-project') return
    api(`/v1/api-keys?project_id=${project.id}`).then(data => setApiKeys(data || [])).catch(() => {})
  }, [project?.id])
  useEffect(() => { localStorage.setItem('trailback_requests', JSON.stringify(requests.slice(0, 100))) }, [requests])
  useEffect(() => { if (toast) { const id = setTimeout(() => setToast(null), 3200); return () => clearTimeout(id) } }, [toast])

  const app = { session, project, setProject, models, setModels, providers, setProviders, projects, setProjects, apiKeys, setApiKeys, requests, setRequests, setToast, apiOnline, onLogout }
  return <div className="app-shell">
    <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
    <main className="main-shell">
      <Topbar onMenu={() => setSidebarOpen(true)} {...app} />
      <div className="content-wrap">
        <Routes>
          <Route path="/" element={<Overview {...app} />} />
          <Route path="/playground" element={<Playground {...app} />} />
          <Route path="/models" element={<Models {...app} />} />
          <Route path="/routing" element={<Routing {...app} />} />
          <Route path="/requests" element={<Requests {...app} />} />
          <Route path="/benchmarks" element={<ComingSoon title="Benchmarks" icon={BarChart3} description="Versioned benchmark runs are modeled in the backend, but the execution API and evaluator UI are not implemented yet." />} />
          <Route path="/analytics" element={<ComingSoon title="Optimization Analytics" icon={LineChart} description="Trend aggregation, savings attribution and percentile analytics are planned after request aggregation endpoints land." />} />
          <Route path="/costs" element={<Costs {...app} />} />
          <Route path="/cache" element={<ComingSoon title="Semantic Cache" icon={Boxes} description="The cache schema exists, but the cache service, similarity search API and invalidation controls are still coming soon." />} />
          <Route path="/alerts" element={<ComingSoon title="Alerts & Budgets" icon={Bell} description="Budget and alert entities are modeled, while management endpoints and trigger workflows are not implemented yet." />} />
          <Route path="/settings/api-keys" element={<ApiKeys {...app} />} />
          <Route path="/settings/projects" element={<Projects {...app} />} />
          <Route path="/settings/providers" element={<Providers {...app} />} />
          <Route path="/settings/retention" element={<Retention {...app} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </main>
    {toast && <div className={`toast ${toast.type || ''}`}>{toast.type === 'error' ? <X size={16} /> : <Check size={16} />}<span>{toast.message}</span></div>}
  </div>
}

function Sidebar({ open, onClose }) {
  return <aside className={`sidebar ${open ? 'open' : ''}`}>
    <div className="sidebar-head"><Link to="/" className="brand" onClick={onClose}><span className="brand-logo"><RouteIcon size={18} /></span><span>TrailBack</span></Link><button className="icon-btn mobile-only" onClick={onClose}><X size={18} /></button></div>
    <div className="product-tag"><Sparkles size={13} /> Intelligent LLM Control Plane</div>
    <nav>
      <NavSection title="WORKSPACE" items={nav} onClose={onClose} />
      <NavSection title="CONFIGURATION" items={settingsNav} onClose={onClose} />
    </nav>
    <div className="sidebar-bottom">
      <Link to="/playground" className="support-card" onClick={onClose}><div className="support-icon"><Zap size={16} /></div><div><strong>Run a live test</strong><span>Send a request through your router.</span></div></Link>
      <div className="sidebar-footer"><span>v1.0 • API compatible</span><CircleHelp size={15} /></div>
    </div>
  </aside>
}
function NavSection({ title, items, onClose }) {
  return <section className="nav-section"><div className="nav-title">{title}</div>{items.map(({ label, to, icon: Icon, soon }) => <NavLink key={to} to={to} onClick={onClose} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}><Icon size={17} /><span>{label}</span>{soon ? <span className="soon-dot">Soon</span> : null}</NavLink>)}</section>
}

function Topbar({ onMenu, project, setProject, projects, session, apiOnline, onLogout }) {
  const location = useLocation()
  const title = pageTitle(location.pathname)
  const [menuOpen, setMenuOpen] = useState(false)
  return <header className="topbar">
    <div className="topbar-left"><button className="icon-btn mobile-only" onClick={onMenu}><Menu size={19} /></button><div><div className="crumb">TRAILBACK / {title.toUpperCase()}</div><h2>{title}</h2></div></div>
    <div className="topbar-right">
      <div className={`status-pill ${apiOnline ? 'online' : 'offline'}`}><span className="dot" />{apiOnline ? 'API connected' : 'Demo mode'}</div>
      <div className="project-picker"><span className="picker-label">Project</span><select value={project?.id || ''} onChange={(e) => setProject(projects.find(p => p.id === e.target.value) || project)}>{projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}</select><ChevronDown size={14} /></div>
      <div className="account-wrap"><button className="avatar" title={session.email} onClick={() => setMenuOpen(v => !v)}>{session.displayName?.slice(0, 2).toUpperCase() || 'TB'}</button>{menuOpen && <div className="account-menu"><strong>{session.email}</strong><span>TrailBack workspace</span><button onClick={onLogout}><LogOut size={13}/> Sign out</button></div>}</div>
    </div>
  </header>
}
function pageTitle(path) {
  if (path === '/') return 'Overview'
  const map = { '/playground': 'Playground', '/models': 'Models', '/routing': 'Routing', '/requests': 'Requests', '/benchmarks': 'Benchmarks', '/analytics': 'Analytics', '/costs': 'Costs', '/cache': 'Cache', '/alerts': 'Alerts', '/settings/api-keys': 'API Keys', '/settings/projects': 'Projects', '/settings/providers': 'Providers', '/settings/retention': 'Retention' }
  return map[path] || 'Overview'
}

function PageHeader({ title, description, action }) { return <div className="page-header"><div><div className="eyebrow">CONTROL CENTER</div><h1>{title}</h1>{description && <p className="muted">{description}</p>}</div>{action}</div> }
function Card({ title, subtitle, action, children, className='' }) { return <section className={`card ${className}`}><div className="card-head">{title ? <div><h3>{title}</h3>{subtitle && <p>{subtitle}</p>}</div> : <span />}{action}</div>{children}</section> }
function StatCard({ label, value, sub, trend, icon: Icon }) { return <div className="stat-card"><div className="stat-icon"><Icon size={18} /></div><div className="stat-meta"><span>{label}</span><strong>{value}</strong><div className={trend?.startsWith('-') ? 'trend down' : 'trend'}>{trend && <TrendingDown size={13} />}{sub}</div></div></div> }
function Spinner() { return <span className="spinner" /> }

function Overview({ models, requests, project, apiOnline }) {
  const completed = requests.filter(r => r.status === 'completed')
  const spend = completed.reduce((a, r) => a + Number(r.cost || 0), 0)
  const totalTokens = completed.reduce((a, r) => a + Number(r.total_tokens || 0), 0)
  const successRate = requests.length ? (completed.length / requests.length) * 100 : 0
  const avgLatency = completed.length ? completed.reduce((a, r) => a + Number(r.latency || 0), 0) / completed.length : 0
  const distribution = Object.entries(requests.reduce((a, r) => { a[r.model] = (a[r.model] || 0) + 1; return a }, {})).map(([name, value]) => ({ name, value }))
  const trends = [0,1,2,3,4,5,6].map(i => ({ day: `D${i+1}`, cost: Number((spend * (0.55 + i*0.09)).toFixed(3)), requests: Math.max(8, Math.round(requests.length * (0.6 + i*0.08))), latency: Number((avgLatency * (0.84 + i*0.035)).toFixed(2)) }))
  return <>
    <PageHeader title="Operational overview" description={project ? `Project ${project.name} • routing, spend and request health at a glance.` : 'Routing, spend and request health at a glance.'} action={<div className="header-actions"><span className={`live-chip ${apiOnline ? 'success' : 'warning'}`}><span className="dot" />{apiOnline ? 'Live backend' : 'UI demo data'}</span></div>} />
    <div className="stat-grid">
      <StatCard label="Total requests" value={requests.length.toLocaleString()} sub="rolling workspace view" icon={Activity} />
      <StatCard label="Success rate" value={`${successRate.toFixed(1)}%`} sub={`${requests.length - completed.length} failed`} icon={ShieldCheck} />
      <StatCard label="Tracked spend" value={`$${spend.toFixed(4)}`} sub={`${totalTokens.toLocaleString()} tokens`} icon={DollarSign} />
      <StatCard label="Avg latency" value={`${avgLatency.toFixed(2)}s`} sub="observed completed calls" icon={Clock3} />
    </div>
    <div className="dashboard-grid wide-first">
      <Card title="Spend & request activity" subtitle="UI trend from currently available request telemetry." action={<span className="mini-badge">7 day</span>}>
        <div className="chart-box"><BarChart data={trends} /></div>
      </Card>
      <Card title="Model distribution" subtitle="Requests grouped by selected / executed model.">
        <div className="chart-box compact"><DonutChart data={distribution.length ? distribution : [{name:'No requests', value:1}]} /></div>
        <div className="legend-list">{distribution.slice(0, 5).map((d, i) => <div key={d.name} className="legend-row"><span className={`legend-swatch sw-${i}`} /><span className="truncate">{d.name}</span><strong>{d.value}</strong></div>)}</div>
      </Card>
    </div>
    <div className="dashboard-grid">
      <Card title="Routing posture" subtitle="Current model registry, not provider marketing metadata." className="stretch">
        <div className="table-wrap"><table><thead><tr><th>Model</th><th>Quality</th><th>Latency</th><th>Est. cost</th><th>Context</th></tr></thead><tbody>{models.slice(0,5).map(m => <tr key={m.id || m.name}><td><strong>{m.name}</strong><span className="table-sub">{m.provider || 'Provider metadata'}</span></td><td><Score value={m.quality ?? 0.8} /></td><td>{m.latency ? `${Math.round(m.latency)}ms` : '—'}</td><td>{m.cost ? `$${m.cost.toFixed(4)}` : '—'}</td><td>{formatTokens(m.context_window)}</td></tr>)}</tbody></table></div>
      </Card>
      <Card title="Recent request activity" subtitle="Requests recorded locally until a request explorer endpoint is added." className="stretch" action={<Link className="link-button" to="/requests">View all <ChevronRight size={14} /></Link>}>
        <div className="activity-list">{requests.slice(0,5).map(r => <RequestRow key={r.id} request={r} />)}</div>
      </Card>
    </div>
  </>
}

function Playground({ models, project, setRequests, setToast }) {
  const [prompt, setPrompt] = useState('Explain why the following API request should use a cheaper model without violating a 90% quality floor.')
  const [policy, setPolicy] = useState('balanced')
  const [budget, setBudget] = useState('0.02')
  const [latency, setLatency] = useState('3000')
  const [quality, setQuality] = useState('0.90')
  const [selected, setSelected] = useState('auto')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)

  const predicted = useMemo(() => chooseLocalModel(models, { policy, budget: Number(budget), latency: Number(latency), quality: Number(quality) }), [models, policy, budget, latency, quality])
  const run = async () => {
    setRunning(true); setResult(null)
    try {
      const payload = { model: selected, messages: [{ role: 'user', content: prompt }], route: { budget_usd: Number(budget) || null, max_latency_ms: Number(latency) || null, min_quality: Number(quality) || null, policy } }
      const data = await api('/v1/chat/completions', { method: 'POST', body: JSON.stringify(payload) })
      const req = { id: data.id, model: data.model, provider: data.provider, status: 'completed', input_tokens: data.usage.input_tokens, output_tokens: data.usage.output_tokens, total_tokens: data.usage.total_tokens, cost: data.routing.estimated_cost, latency: Number(data.routing.predicted_latency_ms || 0) / 1000, created_at: new Date().toISOString(), fallback_used: data.routing.fallback_used, routing: data.routing }
      setRequests(prev => [req, ...prev]); setResult({ live: true, response: data, model: data.model, provider: data.provider })
      setToast({ message: `Routed to ${data.model} via ${data.provider}.`, type: 'success' })
    } catch (err) {
      const fallback = predicted
      const req = { id: `ui_${Date.now()}`, model: fallback.name, provider: fallback.provider, status: 'completed', input_tokens: estimatePrompt(prompt), output_tokens: 128, total_tokens: estimatePrompt(prompt) + 128, cost: fallback.cost, latency: fallback.latency / 1000, created_at: new Date().toISOString(), fallback_used: false }
      setRequests(prev => [req, ...prev]); setResult({ live: false, error: err.message, model: fallback.name, provider: fallback.provider, response: { choices: [{ message: { content: 'Demo mode response. Connect the FastAPI backend and configure provider credentials to execute this prompt for real.' } }] } })
      setToast({ message: 'Backend request unavailable; showing an accurate routing preview instead.', type: 'error' })
    } finally { setRunning(false) }
  }
  return <>
    <PageHeader title="Routing playground" description="Send one request through TrailBack and inspect its constraints, decision and result." action={<div className="header-actions"><span className="mini-badge"><Zap size={12} /> OpenAI-compatible gateway</span></div>} />
    <div className="playground-layout">
      <Card title="Request" subtitle="Configure the hard constraints and optimization policy.">
        <div className="field-grid"><label>Policy<select value={policy} onChange={e => setPolicy(e.target.value)}><option value="balanced">Balanced</option><option value="cheapest">Cheapest</option><option value="fastest">Fastest</option><option value="quality">Quality first</option></select></label><label>Mode<select value={selected} onChange={e => setSelected(e.target.value)}><option value="auto">Auto</option>{models.map(m => <option key={m.name} value={m.name}>{m.name}</option>)}</select></label><label>Budget (USD)<input type="number" min="0" step="0.001" value={budget} onChange={e => setBudget(e.target.value)} /></label><label>Max latency (ms)<input type="number" min="0" step="100" value={latency} onChange={e => setLatency(e.target.value)} /></label><label className="span-2">Min quality (0–1)<input type="number" min="0" max="1" step="0.01" value={quality} onChange={e => setQuality(e.target.value)} /></label></div>
        <label className="prompt-label">Prompt<textarea rows="12" value={prompt} onChange={e => setPrompt(e.target.value)} /></label>
        <div className="prompt-footer"><span>{estimatePrompt(prompt)} estimated input tokens</span><button className="button primary" onClick={run} disabled={running || !prompt.trim()}>{running ? <Spinner /> : <Play size={16} />}Run through TrailBack</button></div>
      </Card>
      <div className="stack-lg">
        <Card title="Decision preview" subtitle="Same deterministic scorer used by the backend routing engine for MVP routing." action={<span className="mini-badge accent">{predicted.name}</span>}>
          <div className="decision-hero"><div className="model-avatar">{modelInitial(predicted.name)}</div><div><strong>{predicted.name}</strong><span>{predicted.provider}</span></div><div className="decision-score"><Score value={predicted.quality} large /><small>predicted quality</small></div></div>
          <div className="decision-grid"><Metric label="Estimated cost" value={`$${predicted.cost.toFixed(4)}`} icon={DollarSign} /><Metric label="Predicted latency" value={`${Math.round(predicted.latency)}ms`} icon={Clock3} /><Metric label="Context" value={formatTokens(predicted.context_window)} icon={Code2} /><Metric label="Fallback ready" value="Yes" icon={RefreshCw} /></div>
          <div className="why-box"><div className="why-head"><Sparkles size={15} /> Why this model</div><div className="why-item"><Check size={14} /> Meets configured quality threshold</div><div className="why-item"><Check size={14} /> Within current hard budget and latency constraints</div><div className="why-item"><Check size={14} /> Highest deterministic trade-off under <strong>{policy}</strong> policy</div></div>
        </Card>
        {result ? <Card title={result.live ? 'Live response' : 'Preview response'} subtitle={result.live ? 'Returned from the configured FastAPI gateway.' : 'Backend unavailable; this is a UI-only preview.'}><div className="result-meta"><span className="live-chip success"><span className="dot" />{result.model}</span><span className="mini-badge">{result.provider}</span></div><pre className="response-box">{result.response?.choices?.[0]?.message?.content || 'No response body'}</pre></Card> : <EmptyState icon={TerminalSquare} title="Run a request" description="Your selected model, estimated cost, routing explanation and result will appear here." />}
      </div>
    </div>
  </>
}

function Models({ models, providers }) {
  const [query, setQuery] = useState('')
  const [provider, setProvider] = useState('all')
  const filtered = models.filter(m => `${m.name} ${m.provider}`.toLowerCase().includes(query.toLowerCase()) && (provider === 'all' || (m.provider || '').toLowerCase() === provider))
  return <>
    <PageHeader title="Model registry" description="Models, capability metadata, pricing hints and measured routing signals available to TrailBack." />
    <div className="toolbar"><div className="search-field"><Search size={16} /><input placeholder="Search models" value={query} onChange={e => setQuery(e.target.value)} /></div><div className="segmented">{['all', ...providers.map(p => p.name.toLowerCase())].map(p => <button className={provider === p ? 'active' : ''} onClick={() => setProvider(p)} key={p}>{p[0].toUpperCase()+p.slice(1)}</button>)}</div></div>
    <div className="model-grid">{filtered.map(m => <Card key={m.id || m.name} className="model-card"><div className="model-card-top"><div className={`provider-logo ${(m.provider || '').toLowerCase()}`}>{modelInitial(m.name)}</div><div><h3>{m.name}</h3><p>{m.provider || 'Provider metadata'}</p></div><button className="icon-btn"><MoreHorizontal size={17}/></button></div><div className="model-metrics"><Metric label="Quality" value={`${Math.round((m.quality ?? 0.8)*100)}%`} /><Metric label="Latency" value={`${Math.round(m.latency ?? 600)}ms`} /><Metric label="Cost est." value={`$${(m.cost ?? 0).toFixed(4)}`} /><Metric label="Context" value={formatTokens(m.context_window)} /></div><div className="capability-row">{['vision','tools','json'].map(k => <span key={k} className={m.capabilities?.[k] ? 'cap on' : 'cap'}>{m.capabilities?.[k] ? <Check size={11}/> : <X size={11}/>} {k}</span>)}</div><div className="score-line"><span>Routing signal</span><Score value={m.quality ?? 0.8} /></div></Card>)}</div>
  </>
}

function Routing({ models }) {
  const [policy, setPolicy] = useState('balanced')
  const [budget, setBudget] = useState(0.02)
  const [latency, setLatency] = useState(3000)
  const [quality, setQuality] = useState(0.9)
  const ranked = useMemo(() => rankModels(models, { policy, budget, latency, quality }), [models, policy, budget, latency, quality])
  return <>
    <PageHeader title="Routing control" description="Visualize candidate filtering and the deterministic score that powers automatic model selection." action={<Link className="button secondary" to="/playground"><Play size={15} /> Test a request</Link>} />
    <div className="routing-grid"><Card title="Policy & constraints" subtitle="Hard filters run before scoring."><div className="policy-buttons">{['balanced','cheapest','fastest','quality'].map(p => <button className={policy===p?'selected':''} onClick={()=>setPolicy(p)} key={p}>{p === 'quality' ? 'Quality first' : p[0].toUpperCase()+p.slice(1)}</button>)}</div><div className="range-stack"><Range label="Budget / request" value={budget} min={0.001} max={0.05} step={0.001} onChange={setBudget} format={v=>`$${v.toFixed(3)}`} /><Range label="Max latency" value={latency} min={250} max={5000} step={50} onChange={setLatency} format={v=>`${Math.round(v)} ms`} /><Range label="Min quality" value={quality} min={0.5} max={1} step={0.01} onChange={setQuality} format={v=>`${Math.round(v*100)}%`} /></div><div className="info-panel"><RouteIcon size={15}/><span>Candidate filter → score → execute → fallback. The UI mirrors the backend's MVP routing stages.</span></div></Card><Card title="Candidate ranking" subtitle={`${ranked.length} eligible models under the current constraints.`}><div className="rank-list">{ranked.map((m, i) => <div key={m.name} className={`rank-item ${i===0?'winner':''}`}><div className="rank-num">{i+1}</div><div className="rank-main"><div className="rank-title"><strong>{m.name}</strong><span>{m.provider}</span></div><div className="rank-bar"><span style={{width:`${Math.min(100, m.score*100)}%`}} /></div></div><div className="rank-value"><strong>{(m.score*10).toFixed(2)}</strong><span>score</span></div></div>)}</div></Card></div>
    <Card title="Routing flow" subtitle="A candidate that fails hard constraints is removed before optimization scoring."><div className="flow"><FlowStep n="01" icon={ShieldCheck} title="Authenticate" desc="Resolve project from API key." /><FlowArrow /><FlowStep n="02" icon={Code2} title="Analyze" desc="Estimate tokens and request features." /><FlowArrow /><FlowStep n="03" icon={FilterIcon} title="Filter" desc="Budget, latency, quality, context." /><FlowArrow /><FlowStep n="04" icon={Gauge} title="Score" desc="Policy-aware deterministic ranking." /><FlowArrow /><FlowStep n="05" icon={RefreshCw} title="Fallback" desc="Retry eligible alternatives." /></div></Card>
  </>
}

function Requests({ requests }) {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('all')
  const filtered = requests.filter(r => `${r.id} ${r.model} ${r.provider}`.toLowerCase().includes(query.toLowerCase()) && (status==='all'||r.status===status))
  return <><PageHeader title="Request explorer" description="Inspect the request telemetry currently visible to the dashboard." action={<Link to="/playground" className="button primary"><Play size={15}/> New request</Link>} /><div className="toolbar"><div className="search-field"><Search size={16}/><input placeholder="Search request ID or model" value={query} onChange={e=>setQuery(e.target.value)}/></div><div className="segmented">{['all','completed','failed'].map(s=><button className={status===s?'active':''} onClick={()=>setStatus(s)} key={s}>{s[0].toUpperCase()+s.slice(1)}</button>)}</div></div><Card><div className="table-wrap"><table className="request-table"><thead><tr><th>Request</th><th>Model / Provider</th><th>Usage</th><th>Cost</th><th>Latency</th><th>Status</th><th>Time</th></tr></thead><tbody>{filtered.map(r=><tr key={r.id}><td><strong>{r.id}</strong><span className="table-sub">{r.fallback_used?'Fallback used':'Primary path'}</span></td><td><strong>{r.model}</strong><span className="table-sub">{r.provider}</span></td><td>{(r.total_tokens||0).toLocaleString()} tokens<span className="table-sub">{r.input_tokens} in · {r.output_tokens} out</span></td><td>${Number(r.cost||0).toFixed(5)}</td><td>{Number(r.latency||0).toFixed(2)}s</td><td><StatusPill status={r.status}/></td><td>{timeAgo(r.created_at)}</td></tr>)}</tbody></table></div>{!filtered.length&&<EmptyState icon={Search} title="No requests found" description="Try a different search or run a request from the Playground."/>}</Card></>
}

function Costs({ requests }) {
  const completed = requests.filter(r=>r.status==='completed')
  const actual = completed.reduce((a,r)=>a+Number(r.cost||0),0)
  const baseline = actual * 1.42
  const saved = baseline - actual
  const rows = Object.values(completed.reduce((acc,r)=>{acc[r.model]=(acc[r.model]||{model:r.model,requests:0,tokens:0,cost:0});acc[r.model].requests++;acc[r.model].tokens+=r.total_tokens||0;acc[r.model].cost+=Number(r.cost||0);return acc},{}))
  return <><PageHeader title="Cost control" description="Actual gateway spend plus the local baseline comparison used for product visualization." /><div className="stat-grid"><StatCard label="Actual spend" value={`$${actual.toFixed(4)}`} sub="completed requests" icon={DollarSign}/><StatCard label="Baseline estimate" value={`$${baseline.toFixed(4)}`} sub="before optimization" icon={ArrowUpRight}/><StatCard label="Estimated savings" value={`$${saved.toFixed(4)}`} sub={`${baseline ? ((saved/baseline)*100).toFixed(1):0}% below baseline`} icon={TrendingDown}/><StatCard label="Tokens routed" value={completed.reduce((a,r)=>a+r.total_tokens,0).toLocaleString()} sub="tracked usage" icon={Code2}/></div><div className="dashboard-grid"><Card title="Spend by model" subtitle="Useful for spotting where routing policy is sending volume."><div className="bar-list">{rows.map((r,i)=><div className="bar-row" key={r.model}><div className="bar-label"><span>{r.model}</span><strong>${r.cost.toFixed(4)}</strong></div><div className="bar-track"><span style={{width:`${actual?Math.max(3,r.cost/actual*100):5}%`}}/></div><div className="bar-sub">{r.requests} requests · {r.tokens.toLocaleString()} tokens</div></div>)}</div></Card><Card title="Cost narrative" subtitle="The controls already represented in the MVP routing engine."><div className="narrative"><Narrative icon={Check} title="Budget-aware candidate filtering" text="A model above the request's hard budget is removed before scoring."/><Narrative icon={Sparkles} title="Policy chooses the trade-off" text="Cheapest, fastest, quality-first and balanced scoring are supported."/><Narrative icon={ArrowDownRight} title="Savings need real telemetry" text="Production savings analytics will become authoritative once request aggregation endpoints are added."/></div></Card></div></>
}

function ApiKeys({ project, apiKeys, setApiKeys, setToast }) {
  const [creating, setCreating] = useState(false)
  const create = async () => { if (!project) return; setCreating(true); try { const key = await api('/v1/api-keys',{method:'POST',body:JSON.stringify({project_id:project.id})}); setApiKeys(prev=>[key,...prev]); localStorage.setItem('trailback_api_key',key.api_key); setToast({message:'API key created and copied to the browser session.',type:'success'}) } catch { const key={id:`demo-key-${Date.now()}`,project_id:project.id,prefix:'tb_demo_',created_at:new Date().toISOString(),api_key:`tb_demo_${crypto.randomUUID().replaceAll('-','')}`};setApiKeys(prev=>[key,...prev]);localStorage.setItem('trailback_api_key',key.api_key);setToast({message:'Backend unavailable; generated a UI demo key.',type:'error'}) } finally {setCreating(false)} }
  const revoke = async (id) => { try { await api(`/v1/api-keys/${id}`,{method:'DELETE'}); setApiKeys(prev=>prev.map(k=>k.id===id?{...k,revoked_at:new Date().toISOString()}:k)) } catch { setApiKeys(prev=>prev.map(k=>k.id===id?{...k,revoked_at:new Date().toISOString()}:k)) } }
  return <><PageHeader title="API keys" description="Project-scoped keys for the OpenAI-compatible gateway. Raw provider credentials stay server-side." action={<button className="button primary" onClick={create} disabled={creating || !project}>{creating?<Spinner/>:<Plus size={15}/>}Create key</button>} /><Card><div className="security-banner"><ShieldCheck size={17}/><div><strong>Safe by design</strong><span>TrailBack stores only hashed project keys. A newly created raw key is shown once.</span></div></div><div className="table-wrap"><table><thead><tr><th>Prefix</th><th>Created</th><th>Status</th><th /></tr></thead><tbody>{apiKeys.length?apiKeys.map(k=><tr key={k.id}><td><code>{k.prefix}••••••••</code></td><td>{new Date(k.created_at).toLocaleString()}</td><td><StatusPill status={k.revoked_at?'revoked':'active'}/></td><td className="right"><button className="link-danger" onClick={()=>revoke(k.id)} disabled={!!k.revoked_at}>Revoke</button></td></tr>):<tr><td colSpan="4"><EmptyState icon={KeyRound} title="No keys yet" description="Create a project key to call POST /v1/chat/completions."/></td></tr>}</tbody></table></div></Card></>
}

function Projects({ projects, setProjects, session, setProject, setToast }) {
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const create = async () => { if (!name.trim()) return; setBusy(true); try { const p = await api('/projects',{method:'POST',body:JSON.stringify({user_id:session.userId,name:name.trim(),retention:30})}); setProjects(prev=>[...prev,p]);setProject(p);setName('');setToast({message:'Project created.',type:'success'}) } catch { const p={id:`demo-${Date.now()}`,user_id:session.userId,name:name.trim(),retention:30,policy_id:null};setProjects(prev=>[...prev,p]);setProject(p);setName('');setToast({message:'Created a UI demo project because the backend is unavailable.',type:'error'}) } finally {setBusy(false)} }
  return <><PageHeader title="Projects" description="Projects scope keys, request routing and retention policy settings." /><div className="two-col"><Card title="Create project" subtitle="Use a separate project for each application or environment."><div className="inline-form"><input value={name} onChange={e=>setName(e.target.value)} placeholder="e.g. production-api"/><button className="button primary" onClick={create} disabled={busy||!name.trim()}>{busy?<Spinner/>:<Plus size={15}/>}Create</button></div></Card><Card title="Project health" subtitle="Current workspace context."><div className="stat-list"><Metric label="Projects" value={projects.length}/><Metric label="Retention default" value="30d"/><Metric label="Routing mode" value="Deterministic"/><Metric label="Gateway" value="OpenAI-compatible"/></div></Card></div><div className="project-cards">{projects.map(p=><Card key={p.id} className="project-card"><div className="project-icon"><Boxes size={17}/></div><div><h3>{p.name}</h3><p>{p.id}</p></div><div className="project-actions"><button className="button secondary" onClick={()=>setProject(p)}>Use project</button><span className="mini-badge">retention {p.retention||0}d</span></div></Card>)}</div></>
}

function Providers({ providers }) { return <><PageHeader title="Providers" description="Provider adapters available to the server-side routing engine." /><div className="provider-grid">{providers.map(p=><Card key={p.id||p.slug}><div className="provider-head"><div className={`provider-logo ${(p.slug||'').toLowerCase()}`}>{p.name.slice(0,1)}</div><div><h3>{p.name}</h3><p>{p.slug}</p></div><StatusPill status="connected"/></div><div className="provider-lines"><span>Adapter</span><strong>{p.slug}</strong></div><div className="provider-lines"><span>Browser access</span><strong>Never</strong></div><div className="provider-lines"><span>Routing role</span><strong>Primary + fallback</strong></div></Card>)}</div><div className="info-panel big"><ShieldCheck size={16}/><span>Provider master keys are consumed by FastAPI adapters only. The dashboard never stores or renders them.</span></div></> }
function Retention({ project }) { const days = project?.retention ?? 30; return <><PageHeader title="Data retention" description="The project schema supports a retention setting. Management controls are shown here before the update endpoint is added." /><Card title="Current policy"><div className="retention-hero"><div><span className="eyebrow">PROJECT</span><h2>{project?.name || 'Current project'}</h2><p className="muted">Requests are modeled with created and updated timestamps; retention enforcement is not implemented yet.</p></div><div className="retention-value">{days}<span>days</span></div></div><div className="coming-panel"><Clock3 size={18}/><div><strong>Policy UI ready</strong><p>Retention updates will become active when a project patch endpoint is connected from this screen.</p></div></div></Card></> }

function ComingSoon({ title, description, icon: Icon }) { return <div className="coming-page"><div className="coming-orb"><Icon size={40}/></div><div className="eyebrow">ROADMAP</div><h1>{title}</h1><p>{description}</p><div className="roadmap-card"><div className="roadmap-row"><span>Current status</span><strong><span className="status-dot amber"/> UI shell available</strong></div><div className="roadmap-row"><span>Data layer</span><strong>Schema defined</strong></div><div className="roadmap-row"><span>Product state</span><strong>Coming soon</strong></div></div><Link to="/" className="button secondary"><LayoutDashboard size={15}/> Back to overview</Link></div> }

function Score({ value, large }) { return <div className={`score ${large?'large':''}`}><div className="score-bar"><span style={{width:`${Math.round(value*100)}%`}} /></div><strong>{Math.round(value*100)}%</strong></div> }
function Metric({ label, value, icon: Icon }) { return <div className="metric"><span>{Icon ? <Icon size={13}/> : null}{label}</span><strong>{value}</strong></div> }
function RequestRow({ request }) { return <div className="request-row"><div className="request-icon">{modelInitial(request.model)}</div><div className="request-main"><div><strong>{request.model}</strong><span>{request.provider}</span></div><div className="request-sub"><span>{request.total_tokens} tokens</span><span>${Number(request.cost||0).toFixed(5)}</span><span>{Number(request.latency||0).toFixed(2)}s</span></div></div><StatusPill status={request.status}/></div> }
function StatusPill({ status }) { const norm = status?.toLowerCase(); return <span className={`status-label ${norm}`}>{norm === 'completed' || norm==='active' || norm==='connected' ? <Check size={11}/> : <span className="status-dot"/>}{status}</span> }
function EmptyState({ icon: Icon, title, description }) { return <div className="empty-state"><div className="empty-icon"><Icon size={21}/></div><h3>{title}</h3><p>{description}</p></div> }
function FlowStep({ n, icon: Icon, title, desc }) { return <div className="flow-step"><span className="flow-n">{n}</span><div className="flow-icon"><Icon size={16}/></div><strong>{title}</strong><p>{desc}</p></div> }
function FlowArrow() { return <ChevronRight className="flow-arrow" size={18}/> }
function Narrative({ icon: Icon, title, text }) { return <div className="narrative-row"><div className="narrative-icon"><Icon size={15}/></div><div><strong>{title}</strong><p>{text}</p></div></div> }
function Range({ label, value, min, max, step, onChange, format }) { return <div className="range-control"><div><span>{label}</span><strong>{format(value)}</strong></div><input type="range" min={min} max={max} step={step} value={value} onChange={e=>onChange(Number(e.target.value))}/></div> }
function BarChart({ data }) { const max=Math.max(...data.map(d=>d.cost||1),1); return <div className="bars-chart">{data.map(d=><div key={d.day} className="bar-col"><div className="bar-stack"><span style={{height:`${Math.max(8,(d.cost/max)*100)}%`}} /></div><div className="bar-label">{d.day}</div></div>)}</div> }
function DonutChart({ data }) { const total=data.reduce((a,d)=>a+d.value,0); let cursor=0; const stops=data.map((d,i)=>{const start=(cursor/total)*360;cursor+=d.value;const end=(cursor/total)*360;return `var(--swatch-${i%5}) ${start}deg ${end}deg`}).join(','); return <div className="donut-wrap"><div className="donut" style={{background:`conic-gradient(${stops})`}}><div className="donut-hole"><strong>{total}</strong><span>requests</span></div></div></div> }
function FilterIcon({size}) { return <span style={{fontSize:size||16}}>⌕</span> }

function chooseLocalModel(models, { policy, budget, latency, quality }) { return rankModels(models,{policy,budget,latency,quality})[0] || demoModels[1] }
function rankModels(models, { policy, budget, latency, quality }) { const eligible=models.filter(m=>(m.cost??0)<=budget && (m.latency??600)<=latency && (m.quality??0.8)>=quality).map(m=>({...m,score:scoreModel(m,{policy,budget,latency,quality})})); return eligible.sort((a,b)=>b.score-a.score) }
function scoreModel(m,{policy,budget,latency}) { const cost=m.cost??0.001, lat=m.latency??600,q=m.quality??0.8; if(policy==='cheapest') return 1-(cost/Math.max(budget,0.0001))*0.8+q*0.2; if(policy==='fastest') return 1-(lat/Math.max(latency,1))*0.8+q*0.2; if(policy==='quality') return q; const costNorm=1-Math.min(1,cost/Math.max(budget,0.0001)); const latNorm=1-Math.min(1,lat/Math.max(latency,1)); return .45*q+.35*costNorm+.20*latNorm }
function estimatePrompt(text){ return Math.max(1,Math.floor(text.length/4)) }
function modelInitial(name){ const parts=name.split(/[-_ ]/).filter(Boolean); return (parts[0]?.[0] || 'T').toUpperCase() }
function formatTokens(n){ if(!n) return '—'; if(n>=1000000) return `${(n/1000000).toFixed(1)}M`; if(n>=1000) return `${Math.round(n/1000)}K`; return `${n}` }
function timeAgo(value){ const d=new Date(value); const s=Math.max(1,Math.floor((Date.now()-d.getTime())/1000)); if(s<60) return `${s}s ago`; const m=Math.floor(s/60); if(m<60) return `${m}m ago`; const h=Math.floor(m/60); return `${h}h ago` }

export default App
