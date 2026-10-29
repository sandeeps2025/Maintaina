import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  BrainCircuit,
  CalendarClock,
  CheckCircle2,
  ChevronRight,
  CircleGauge,
  Clock,
  Cpu,
  Database,
  Download,
  Filter,
  Flame,
  Gauge,
  Layers,
  LayoutDashboard,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Printer,
  RefreshCw,
  Search,
  Settings,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Sun,
  Thermometer,
  TrendingDown,
  TrendingUp,
  TriangleAlert,
  Wrench,
  X,
  Zap,
} from "lucide-react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const initialMachines = [
  {
    id: "M-104",
    name: "Primary Compressor Unit",
    area: "Assembly Line Alpha",
    health: 92,
    risk: "LOW",
    rul: 135,
    temp: 58.4,
    pressure: 4.4,
    vibration: 1.6,
    current: 7.9,
    load: 64,
    rpm: 1490,
    voltage: 230,
    humidity: 48,
    status: "Operational",
    component: "Nominal"
  },
  {
    id: "M-087",
    name: "Cryogenic Cooling Pump",
    area: "HVAC Sub-station B",
    health: 76,
    risk: "MEDIUM",
    rul: 68,
    temp: 74.2,
    pressure: 4.9,
    vibration: 3.2,
    current: 9.8,
    load: 79,
    rpm: 1460,
    voltage: 228,
    humidity: 52,
    status: "Inspection Due",
    component: "Cooling Fan"
  },
  {
    id: "M-221",
    name: "High-Torque Motor Assembly",
    area: "Stamping Cell 4",
    health: 48,
    risk: "HIGH",
    rul: 26,
    temp: 86.8,
    pressure: 5.6,
    vibration: 5.9,
    current: 12.4,
    load: 92,
    rpm: 1420,
    voltage: 222,
    humidity: 55,
    status: "Degraded",
    component: "Drive Bearings"
  },
  {
    id: "M-142",
    name: "Hydraulic Actuator Pump",
    area: "Heavy Press Yard",
    health: 89,
    risk: "LOW",
    rul: 180,
    temp: 61.0,
    pressure: 4.3,
    vibration: 1.8,
    current: 8.1,
    load: 62,
    rpm: 1510,
    voltage: 231,
    humidity: 46,
    status: "Operational",
    component: "Nominal"
  },
  {
    id: "M-315",
    name: "CNC 5-Axis Milling Spindle",
    area: "Precision Machining",
    health: 83,
    risk: "LOW",
    rul: 112,
    temp: 64.5,
    pressure: 4.1,
    vibration: 2.2,
    current: 8.6,
    load: 71,
    rpm: 3600,
    voltage: 230,
    humidity: 44,
    status: "Operational",
    component: "Nominal"
  },
  {
    id: "M-409",
    name: "Exhaust Turbo Blower",
    area: "Ventilation Tunnel",
    health: 62,
    risk: "MEDIUM",
    rul: 45,
    temp: 79.1,
    pressure: 3.8,
    vibration: 3.8,
    current: 10.5,
    load: 84,
    rpm: 1440,
    voltage: 226,
    humidity: 60,
    status: "Warning",
    component: "Impeller Seals"
  },
  {
    id: "M-512",
    name: "Robotic Welding Generator",
    area: "Cell D Automated",
    health: 95,
    risk: "LOW",
    rul: 210,
    temp: 54.0,
    pressure: 4.2,
    vibration: 1.2,
    current: 7.2,
    load: 55,
    rpm: 1500,
    voltage: 232,
    humidity: 42,
    status: "Optimal",
    component: "Nominal"
  },
  {
    id: "M-630",
    name: "Main Turbine Lubricator",
    area: "Power Plant Wing",
    health: 38,
    risk: "CRITICAL",
    rul: 12,
    temp: 92.5,
    pressure: 6.4,
    vibration: 6.8,
    current: 14.1,
    load: 96,
    rpm: 1390,
    voltage: 218,
    humidity: 62,
    status: "Critical Alert",
    component: "Pressure Relief Valve"
  }
];

const telemetryTrend = [68, 71, 70, 74, 73, 78, 76, 82, 80, 85, 84, 88, 86, 91, 89, 93, 91, 94];

function riskClass(risk) {
  const r = String(risk || "").toLowerCase();
  if (r.includes("high") || r.includes("critical")) return "risk-high";
  if (r.includes("med") || r.includes("warn")) return "risk-medium";
  return "risk-low";
}

function healthTone(score) {
  if (score < 55) return "danger";
  if (score < 78) return "warning";
  return "good";
}

export default function App() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [machines, setMachines] = useState(initialMachines);
  const [selectedMachine, setSelectedMachine] = useState(initialMachines[0]);
  const [history, setHistory] = useState([]);
  const [apiOnline, setApiOnline] = useState(false);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterRisk, setFilterRisk] = useState("ALL");
  const [liveStreamActive, setLiveStreamActive] = useState(true);

  // Maintenance Work Orders
  const [workOrders, setWorkOrders] = useState([
    { id: "WO-8021", machineId: "M-630", title: "Emergency inspection of relief valve", priority: "Critical", status: "Pending", technician: "Alex Vance", date: "Today" },
    { id: "WO-7994", machineId: "M-221", title: "Bearing lubrication & vibration re-balancing", priority: "Critical", status: "Dispatched", technician: "Maria Santos", date: "Today" },
    { id: "WO-7882", machineId: "M-409", title: "Exhaust impeller balance & seal replacement", priority: "Medium", status: "Scheduled", technician: "Devon Reed", date: "Tomorrow" },
    { id: "WO-7740", machineId: "M-087", title: "Cooling pump heat exchanger flushes", priority: "Medium", status: "Scheduled", technician: "Elena Rostova", date: "In 2 days" },
    { id: "WO-7612", machineId: "M-104", title: "Standard compressor 2,000hr service", priority: "Low", status: "Completed", technician: "Sandeep S", date: "Yesterday" }
  ]);

  // Current interactive sensor state
  const [sensors, setSensors] = useState({
    temperature: 58.4,
    pressure: 4.4,
    vibration: 1.6,
    motor_current: 7.9,
    voltage: 230,
    humidity: 48,
    rpm: 1490,
    load_percentage: 64
  });

  // Dynamic SHAP contributions
  const [shapContributions, setShapContributions] = useState([
    { label: "Vibration Signature", value: 38 },
    { label: "Core Temperature", value: 29 },
    { label: "Pressure Gradient", value: 18 },
    { label: "Motor Current Draw", value: 10 },
    { label: "Dynamic Load Index", value: 5 }
  ]);

  // Sync dark mode class
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  // Auto-dismiss toast
  useEffect(() => {
    if (!toastMessage) return;
    const timer = setTimeout(() => setToastMessage(""), 3500);
    return () => clearTimeout(timer);
  }, [toastMessage]);

  // Fetch API Health & History
  const fetchBackendData = async () => {
    try {
      const res = await fetch(`${API_BASE}/history?limit=30`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setHistory(data);
        }
        setApiOnline(true);
      } else {
        setApiOnline(false);
      }
    } catch {
      setApiOnline(false);
    }
  };

  useEffect(() => {
    fetchBackendData();
    const interval = setInterval(fetchBackendData, 20000);
    return () => clearInterval(interval);
  }, []);

  // When a machine is selected from the fleet
  const handleSelectMachine = (machine) => {
    setSelectedMachine(machine);
    setSensors({
      temperature: machine.temp,
      pressure: machine.pressure,
      vibration: machine.vibration,
      motor_current: machine.current,
      voltage: machine.voltage || 230,
      humidity: machine.humidity || 50,
      rpm: machine.rpm || 1480,
      load_percentage: machine.load
    });
  };

  // Live Jitter Simulation for Industrial Feel
  useEffect(() => {
    if (!liveStreamActive) return;
    const interval = setInterval(() => {
      setMachines((prev) =>
        prev.map((m) => {
          const jitter = (Math.random() - 0.5) * 0.4;
          const tempJitter = (Math.random() - 0.5) * 0.6;
          return {
            ...m,
            vibration: Math.max(0.8, +(m.vibration + jitter * 0.1).toFixed(1)),
            temp: +(m.temp + tempJitter * 0.2).toFixed(1)
          };
        })
      );
    }, 4000);
    return () => clearInterval(interval);
  }, [liveStreamActive]);

  // Run AI Prediction
  const runPrediction = async () => {
    setLoadingPrediction(true);
    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          machine_id: selectedMachine.id,
          ...sensors
        })
      });

      if (!response.ok) throw new Error("API call failed");
      const res = await response.json();

      const newHealth = Number(res.Health_Score ?? res.health_score ?? 85);
      const newRisk = String(res.risk ?? (newHealth < 55 ? "HIGH" : newHealth < 75 ? "MEDIUM" : "LOW")).toUpperCase();
      const newRul = Number(res.RUL ?? res.rul ?? Math.max(12, Math.round(newHealth * 1.6)));
      const newComponent = res.predicted_failure_component || res.Predicted_Failure_Component || selectedMachine.component;

      if (res.shap_contributions && Array.isArray(res.shap_contributions)) {
        setShapContributions(res.shap_contributions);
      }

      const updatedMachine = {
        ...selectedMachine,
        health: newHealth,
        risk: newRisk,
        rul: newRul,
        temp: sensors.temperature,
        pressure: sensors.pressure,
        vibration: sensors.vibration,
        current: sensors.motor_current,
        load: sensors.load_percentage,
        component: newComponent,
        status: newRisk === "LOW" ? "Operational" : newRisk === "MEDIUM" ? "Warning" : "Critical Alert"
      };

      setSelectedMachine(updatedMachine);
      setMachines((prev) => prev.map((m) => (m.id === updatedMachine.id ? updatedMachine : m)));
      setToastMessage(`AI Inference Complete: Machine ${selectedMachine.id} assessed at ${newHealth}% Health (${newRisk} Risk).`);
      setApiOnline(true);
      fetchBackendData();
    } catch {
      // High-fidelity fallback client-side inference model
      const totalStress =
        Math.max(0, (sensors.temperature - 60) * 1.2) +
        Math.max(0, (sensors.vibration - 1.8) * 16) +
        Math.max(0, Math.abs(sensors.pressure - 4.5) * 8) +
        Math.max(0, (sensors.motor_current - 8.5) * 4);

      const calculatedHealth = Math.max(8, Math.min(98, Math.round(100 - totalStress)));
      const calculatedRisk = calculatedHealth >= 78 ? "LOW" : calculatedHealth >= 55 ? "MEDIUM" : "HIGH";
      const calculatedRul = Math.max(8, Math.round(calculatedHealth * 1.5 - sensors.vibration * 6));

      const updated = {
        ...selectedMachine,
        health: calculatedHealth,
        risk: calculatedRisk,
        rul: calculatedRul,
        temp: sensors.temperature,
        pressure: sensors.pressure,
        vibration: sensors.vibration,
        current: sensors.motor_current,
        load: sensors.load_percentage,
        component: sensors.vibration > 4.5 ? "Bearings" : sensors.temperature > 80 ? "Cooling System" : "Routine Wear",
        status: calculatedRisk === "LOW" ? "Operational" : calculatedRisk === "MEDIUM" ? "Warning" : "Critical Alert"
      };

      setSelectedMachine(updated);
      setMachines((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      setToastMessage(`Predictive AI updated in Offline Mode. Health: ${calculatedHealth}%, Risk: ${calculatedRisk}.`);
    } finally {
      setLoadingPrediction(false);
    }
  };

  // Sensor Presets
  const applyPreset = (presetName) => {
    if (presetName === "optimal") {
      setSensors({ temperature: 56.5, pressure: 4.3, vibration: 1.4, motor_current: 7.6, voltage: 231, humidity: 46, rpm: 1500, load_percentage: 58 });
      setToastMessage("Applied preset: Nominal Operating Conditions.");
    } else if (presetName === "thermal") {
      setSensors({ temperature: 86.2, pressure: 4.9, vibration: 2.8, motor_current: 10.4, voltage: 226, humidity: 54, rpm: 1440, load_percentage: 82 });
      setToastMessage("Applied preset: High Thermal Stress Scenario.");
    } else if (presetName === "bearing") {
      setSensors({ temperature: 74.0, pressure: 4.5, vibration: 6.2, motor_current: 12.1, voltage: 224, humidity: 50, rpm: 1410, load_percentage: 90 });
      setToastMessage("Applied preset: Bearing Mechanical Flaw Scenario.");
    } else if (presetName === "critical") {
      setSensors({ temperature: 95.0, pressure: 6.5, vibration: 7.4, motor_current: 14.8, voltage: 216, humidity: 64, rpm: 1380, load_percentage: 98 });
      setToastMessage("Applied preset: Critical Failure Impending.");
    }
  };

  // Fleet Metrics
  const metrics = useMemo(() => {
    const avg = Math.round(machines.reduce((s, m) => s + m.health, 0) / machines.length);
    const high = machines.filter((m) => m.risk === "HIGH" || m.risk === "CRITICAL").length;
    const med = machines.filter((m) => m.risk === "MEDIUM").length;
    const low = machines.filter((m) => m.risk === "LOW").length;
    return { avg, high, med, low };
  }, [machines]);

  // Filtered Machines for Live Monitoring
  const filteredMachines = useMemo(() => {
    return machines.filter((m) => {
      const matchSearch = m.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          m.area.toLowerCase().includes(searchQuery.toLowerCase());
      if (!matchSearch) return false;
      if (filterRisk === "ALL") return true;
      if (filterRisk === "HIGH") return m.risk === "HIGH" || m.risk === "CRITICAL";
      if (filterRisk === "MEDIUM") return m.risk === "MEDIUM";
      if (filterRisk === "LOW") return m.risk === "LOW";
      return true;
    });
  }, [machines, searchQuery, filterRisk]);

  const navItems = [
    { label: "Overview", icon: LayoutDashboard },
    { label: "Live Telemetry", icon: Activity, badge: liveStreamActive },
    { label: "AI Diagnostics", icon: BrainCircuit },
    { label: "Maintenance Queue", icon: CalendarClock },
    { label: "ML Architecture", icon: Layers }
  ];

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : "collapsed"}`}>
        <div className="brand">
          <div className="brand-mark">
            <BrainCircuit size={22} />
          </div>
          {sidebarOpen && (
            <div>
              <div className="brand-title">Maintaina</div>
              <div className="brand-subtitle">Industrial Intelligence</div>
            </div>
          )}
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            title="Toggle Sidebar"
          >
            {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
          </button>
        </div>

        <div className="nav-section">
          {sidebarOpen && <div className="nav-label">COMMAND CENTER</div>}
          {navItems.map(({ label, icon: Icon, badge }) => (
            <button
              key={label}
              className={`nav-item ${activeTab === label ? "active" : ""}`}
              onClick={() => setActiveTab(label)}
              title={label}
            >
              <Icon size={18} />
              {sidebarOpen && <span>{label}</span>}
              {sidebarOpen && badge && <span className="live-dot" />}
            </button>
          ))}
        </div>

        {sidebarOpen && (
          <div className="sidebar-bottom">
            <div className="model-badge-card">
              <div className="icon-box">
                <Sparkles size={16} />
              </div>
              <div>
                <strong>Ensemble AI Core</strong>
                <span>5 Active Models</span>
              </div>
              <ShieldCheck size={16} style={{ color: "var(--success)", marginLeft: "auto" }} />
            </div>

            <div className="user-profile">
              <div className="user-avatar">SS</div>
              <div>
                <strong>Sandeep S</strong>
                <span>Reliability & ML Engineer</span>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Container */}
      <main className="main">
        {/* Topbar */}
        <header className="topbar">
          <div className="mobile-brand">
            <div className="brand-mark" style={{ width: 34, height: 34 }}>
              <BrainCircuit size={18} />
            </div>
            <strong>Maintaina</strong>
          </div>

          <div className="breadcrumb">
            <span>Platform</span>
            <ChevronRight size={14} />
            <strong>{activeTab}</strong>
          </div>

          <div className="top-actions">
            <div className={`connection-pill ${apiOnline ? "online" : ""}`}>
              <span className="dot" />
              <span>{apiOnline ? "FastAPI Online" : "Demo Mode"}</span>
            </div>

            <button
              className="icon-btn"
              title="Refresh Telemetry"
              onClick={() => {
                fetchBackendData();
                setToastMessage("Telemetry and models re-synchronized.");
              }}
            >
              <RefreshCw size={17} />
            </button>

            <button
              className="icon-btn"
              title="Toggle Live Stream Simulation"
              onClick={() => {
                setLiveStreamActive(!liveStreamActive);
                setToastMessage(liveStreamActive ? "Telemetry streaming paused." : "Telemetry streaming active.");
              }}
            >
              <Activity size={17} style={{ color: liveStreamActive ? "var(--success)" : "var(--text-muted)" }} />
            </button>

            <button
              className="icon-btn"
              title="Toggle Dark / Light Theme"
              onClick={() => setDarkMode(!darkMode)}
            >
              {darkMode ? <Sun size={17} /> : <Moon size={17} />}
            </button>
          </div>
        </header>

        {/* Content Views */}
        <div className="content">
          {activeTab === "Overview" && (
            <>
              {/* Hero Banner */}
              <section className="hero">
                <div className="hero-content">
                  <div className="eyebrow">
                    <span className="pulse" />
                    PREDICTIVE MAINTENANCE INTELLIGENCE
                  </div>
                  <h1>
                    Zero Unplanned Downtime.<br />
                    <span>Real-Time AI Telemetry.</span>
                  </h1>
                  <p>
                    Autonomous health scoring, anomaly detection, and remaining useful life (RUL) estimation
                    powered by an industrial ensemble of Random Forest, XGBoost, Isolation Forest, LSTM, and Autoencoders.
                  </p>
                  <div className="hero-actions">
                    <button className="primary-btn" onClick={() => setActiveTab("AI Diagnostics")}>
                      <BrainCircuit size={16} /> Run Diagnostics Lab
                    </button>
                    <button className="secondary-btn" onClick={() => setActiveTab("Live Telemetry")}>
                      <Activity size={16} /> Monitor Machine Fleet
                    </button>
                  </div>
                </div>

                <div className="hero-visual">
                  <div className="hero-ring">
                    <Cpu size={46} />
                  </div>
                  <div className="floating-chip chip-1">
                    <ShieldCheck size={14} style={{ color: "var(--success)" }} />
                    99.4% Uptime Target
                  </div>
                  <div className="floating-chip chip-2">
                    <Zap size={14} style={{ color: "var(--primary)" }} />
                    5 Active ML Engines
                  </div>
                  <div className="floating-chip chip-3">
                    <CircleGauge size={14} style={{ color: "var(--accent-cyan)" }} />
                    Live Edge Telemetry
                  </div>
                </div>
              </section>

              {/* Stat KPIs */}
              <section className="stat-grid">
                <div className="stat-card">
                  <div className="stat-top">
                    <div className="stat-icon">
                      <CircleGauge size={20} />
                    </div>
                    <span className="trend-badge positive">
                      <ArrowUpRight size={13} /> +3.2%
                    </span>
                  </div>
                  <div className="stat-value">{metrics.avg}%</div>
                  <div className="stat-label">Fleet Composite Health Score</div>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <div className="stat-icon" style={{ color: "var(--danger)", background: "var(--danger-bg)" }}>
                      <AlertOctagon size={20} />
                    </div>
                    <span className={`trend-badge ${metrics.high > 0 ? "danger" : "positive"}`}>
                      {metrics.high > 0 ? "Action Required" : "All Clear"}
                    </span>
                  </div>
                  <div className="stat-value">{metrics.high}</div>
                  <div className="stat-label">Critical Anomaly Machines</div>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <div className="stat-icon" style={{ color: "var(--warning)", background: "var(--warning-bg)" }}>
                      <CalendarClock size={20} />
                    </div>
                    <span className="trend-badge">
                      <Clock size={13} /> Next 48 hrs
                    </span>
                  </div>
                  <div className="stat-value">{metrics.med + metrics.high}</div>
                  <div className="stat-label">Scheduled Maintenance Due</div>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <div className="stat-icon" style={{ color: "var(--success)", background: "var(--success-bg)" }}>
                      <TrendingDown size={20} />
                    </div>
                    <span className="trend-badge positive">
                      <TrendingDown size={13} /> -24.8%
                    </span>
                  </div>
                  <div className="stat-value">1.8 hrs</div>
                  <div className="stat-label">Projected Unscheduled Downtime</div>
                </div>
              </section>

              {/* Chart & Risk Distribution */}
              <section className="section-grid">
                {/* Fleet Health Chart */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <h2>Fleet Health Trajectory</h2>
                      <p>Aggregate historical telemetry and model prediction stability</p>
                    </div>
                    <button className="text-btn" onClick={() => setActiveTab("Live Telemetry")}>
                      View Fleet Details <ChevronRight size={14} />
                    </button>
                  </div>

                  <div className="fleet-chart">
                    <div className="chart-y">
                      <span>100%</span>
                      <span>75%</span>
                      <span>50%</span>
                      <span>25%</span>
                      <span>0%</span>
                    </div>

                    <div className="chart-area">
                      <div className="grid-lines">
                        <i /><i /><i /><i />
                      </div>

                      <svg viewBox="0 0 900 240" preserveAspectRatio="none" className="line-chart">
                        <defs>
                          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.35" />
                            <stop offset="100%" stopColor="#4f46e5" stopOpacity="0.0" />
                          </linearGradient>
                        </defs>
                        <path
                          d={`M 0 240 ${telemetryTrend
                            .map((v, i) => `L ${(i / (telemetryTrend.length - 1)) * 900} ${230 - (v / 100) * 200}`)
                            .join(" ")} L 900 240 Z`}
                          fill="url(#chartGradient)"
                        />
                        <path
                          d={telemetryTrend
                            .map((v, i) => `${i ? "L" : "M"} ${(i / (telemetryTrend.length - 1)) * 900} ${230 - (v / 100) * 200}`)
                            .join(" ")}
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                          vectorEffect="non-scaling-stroke"
                        />
                      </svg>

                      <div className="chart-x">
                        <span>00:00</span>
                        <span>06:00</span>
                        <span>12:00</span>
                        <span>18:00</span>
                        <span>Live</span>
                      </div>
                    </div>
                  </div>

                  <div className="chart-footer">
                    <div>
                      <span className="legend-dot" />
                      Continuous 24h Model Health Aggregation
                    </div>
                    <strong>{metrics.avg}% Overall Index</strong>
                  </div>
                </div>

                {/* Risk Distribution */}
                <div className="panel risk-panel">
                  <div className="panel-header">
                    <div>
                      <h2>Risk Distribution</h2>
                      <p>Current industrial fleet categorization</p>
                    </div>
                  </div>

                  <div className="risk-donut">
                    <div className="donut">
                      <div className="donut-inner">
                        <strong>{machines.length}</strong>
                        <span>Assets Active</span>
                      </div>
                    </div>
                  </div>

                  <div className="risk-list">
                    <div className="risk-row">
                      <span><i className="risk-dot low" />Healthy</span>
                      <b>{metrics.low}</b>
                      <div className="mini-track">
                        <i className="low" style={{ width: `${(metrics.low / machines.length) * 100}%` }} />
                      </div>
                      <small>{Math.round((metrics.low / machines.length) * 100)}%</small>
                    </div>

                    <div className="risk-row">
                      <span><i className="risk-dot medium" />Inspection</span>
                      <b>{metrics.med}</b>
                      <div className="mini-track">
                        <i className="medium" style={{ width: `${(metrics.med / machines.length) * 100}%` }} />
                      </div>
                      <small>{Math.round((metrics.med / machines.length) * 100)}%</small>
                    </div>

                    <div className="risk-row">
                      <span><i className="risk-dot high" />Critical</span>
                      <b>{metrics.high}</b>
                      <div className="mini-track">
                        <i className="high" style={{ width: `${(metrics.high / machines.length) * 100}%` }} />
                      </div>
                      <small>{Math.round((metrics.high / machines.length) * 100)}%</small>
                    </div>
                  </div>
                </div>
              </section>

              {/* Machine Fleet Cards */}
              <section className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Industrial Machine Fleet</h2>
                    <p>Select any machine to load its live edge sensor readings into the AI Prediction Engine</p>
                  </div>
                  <button className="text-btn" onClick={() => window.print()}>
                    <Printer size={14} /> Export Fleet Dossier
                  </button>
                </div>

                <div className="machine-grid">
                  {machines.slice(0, 8).map((machine) => (
                    <div
                      key={machine.id}
                      className={`machine-card ${selectedMachine.id === machine.id ? "selected" : ""}`}
                      onClick={() => handleSelectMachine(machine)}
                    >
                      <div className="machine-top">
                        <div className="machine-symbol">
                          <Cpu size={18} />
                        </div>
                        <span className={`risk-pill ${riskClass(machine.risk)}`}>{machine.risk}</span>
                      </div>

                      <div className="machine-id">{machine.id}</div>
                      <div className="machine-name">{machine.name}</div>
                      <div className="machine-area">{machine.area}</div>

                      <div className="machine-health">
                        <div className="health-number">
                          {machine.health}<small>%</small>
                        </div>
                        <div className="health-bar">
                          <i style={{ width: `${machine.health}%` }} />
                        </div>
                      </div>

                      <div className="machine-meta">
                        <span>RUL <b>{machine.rul}h</b></span>
                        <span><Thermometer size={12} /> {machine.temp}°C</span>
                        <span><Activity size={12} /> {machine.vibration} mm/s</span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Prediction & Explainability */}
              <section className="section-grid detail-grid">
                {/* AI Prediction Center */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <h2>AI Prediction Center</h2>
                      <p>Active diagnostic snapshot for {selectedMachine.id} ({selectedMachine.name})</p>
                    </div>
                    <span className={`risk-pill ${riskClass(selectedMachine.risk)}`}>
                      {selectedMachine.status}
                    </span>
                  </div>

                  <div className="prediction-layout">
                    <div className="big-score">
                      <div
                        className="score-ring"
                        style={{
                          background: `conic-gradient(${
                            selectedMachine.health < 55
                              ? "var(--danger)"
                              : selectedMachine.health < 78
                              ? "var(--warning)"
                              : "var(--success)"
                          } ${selectedMachine.health * 3.6}deg, var(--surface-2) 0deg)`
                        }}
                      >
                        <div className="score-inner">
                          <strong>{selectedMachine.health}</strong>
                          <span>Health Index</span>
                        </div>
                      </div>
                      <div className="score-caption">
                        <span className={`status-dot ${healthTone(selectedMachine.health)}`} />
                        {selectedMachine.risk === "LOW"
                          ? "Normal Operating Envelope"
                          : selectedMachine.risk === "MEDIUM"
                          ? "Service Window Approaching"
                          : "Immediate Attention Advised"}
                      </div>
                    </div>

                    <div className="prediction-stats">
                      <div className="prediction-metric">
                        <div className="metric-icon" style={{ color: "var(--danger)" }}>
                          <TriangleAlert size={18} />
                        </div>
                        <div>
                          <small>Failure Probability</small>
                          <strong>{Math.max(2, 100 - selectedMachine.health)}%</strong>
                        </div>
                      </div>

                      <div className="prediction-metric">
                        <div className="metric-icon" style={{ color: "var(--accent-cyan)" }}>
                          <Clock size={18} />
                        </div>
                        <div>
                          <small>Remaining Useful Life (RUL)</small>
                          <strong>{selectedMachine.rul} Hours</strong>
                        </div>
                      </div>

                      <div className="prediction-metric">
                        <div className="metric-icon" style={{ color: "var(--warning)" }}>
                          <Wrench size={18} />
                        </div>
                        <div>
                          <small>Primary Wear Component</small>
                          <strong>{selectedMachine.component}</strong>
                        </div>
                      </div>

                      <div className="prediction-metric">
                        <div className="metric-icon" style={{ color: "var(--primary)" }}>
                          <TrendingDown size={18} />
                        </div>
                        <div>
                          <small>Est. Unscheduled Loss</small>
                          <strong>${intVal(100 - selectedMachine.health) * 24}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Explainable AI (SHAP) */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <h2>Explainable AI (XAI)</h2>
                      <p>SHAP feature contribution to the failure score</p>
                    </div>
                    <Sparkles size={16} style={{ color: "var(--primary)" }} />
                  </div>

                  <div className="explain-intro">
                    <Sparkles size={14} /> TreeExplainer Ensemble Feature Attribution
                  </div>

                  {shapContributions.map((feat) => (
                    <div className="feature-row" key={feat.label}>
                      <div>
                        <span>{feat.label}</span>
                        <b>{feat.value}%</b>
                      </div>
                      <div className="feature-track">
                        <i style={{ width: `${feat.value}%` }} />
                      </div>
                    </div>
                  ))}

                  <div className="ai-note">
                    <BrainCircuit size={16} />
                    <span>
                      The ensemble is heavily weighting <b>vibration harmonics</b> and <b>operating temperature</b>. Corrective mount adjustment or thermal flushing will yield the fastest health recovery.
                    </span>
                  </div>
                </div>
              </section>

              {/* Lower Grid: Sensor Telemetry & Maintenance Queue */}
              <section className="section-grid lower-grid">
                {/* Live Sensor Telemetry */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <h2>Live Sensor Telemetry</h2>
                      <p>Simulate machine stresses or enter edge IoT readings</p>
                    </div>
                  </div>

                  <div className="sensor-presets">
                    <span style={{ fontSize: 11, color: "var(--text-muted)", alignSelf: "center", marginRight: 4 }}>
                      Stress Scenarios:
                    </span>
                    <button className="preset-chip" onClick={() => applyPreset("optimal")}>
                      ✓ Nominal State
                    </button>
                    <button className="preset-chip" onClick={() => applyPreset("thermal")}>
                      🔥 Thermal Overheat
                    </button>
                    <button className="preset-chip" onClick={() => applyPreset("bearing")}>
                      ⚠️ Bearing Flaw
                    </button>
                    <button className="preset-chip" onClick={() => applyPreset("critical")}>
                      🚨 Critical Runout
                    </button>
                  </div>

                  <div className="sensor-grid">
                    <div className="sensor-input">
                      <span><Thermometer size={14} /> Core Temp</span>
                      <div>
                        <input
                          type="number"
                          step="0.5"
                          value={sensors.temperature}
                          onChange={(e) => setSensors({ ...sensors, temperature: Number(e.target.value) })}
                        />
                        <em>°C</em>
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Gauge size={14} /> Fluid Pressure</span>
                      <div>
                        <input
                          type="number"
                          step="0.1"
                          value={sensors.pressure}
                          onChange={(e) => setSensors({ ...sensors, pressure: Number(e.target.value) })}
                        />
                        <em>bar</em>
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Activity size={14} /> Vibration RMS</span>
                      <div>
                        <input
                          type="number"
                          step="0.1"
                          value={sensors.vibration}
                          onChange={(e) => setSensors({ ...sensors, vibration: Number(e.target.value) })}
                        />
                        <em>mm/s</em>
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Zap size={14} /> Motor Current</span>
                      <div>
                        <input
                          type="number"
                          step="0.1"
                          value={sensors.motor_current}
                          onChange={(e) => setSensors({ ...sensors, motor_current: Number(e.target.value) })}
                        />
                        <em>A</em>
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Activity size={14} /> Shaft Speed</span>
                      <div>
                        <input
                          type="number"
                          step="10"
                          value={sensors.rpm}
                          onChange={(e) => setSensors({ ...sensors, rpm: Number(e.target.value) })}
                        />
                        <em>RPM</em>
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Gauge size={14} /> Active Load</span>
                      <div>
                        <input
                          type="number"
                          step="1"
                          value={sensors.load_percentage}
                          onChange={(e) => setSensors({ ...sensors, load_percentage: Number(e.target.value) })}
                        />
                        <em>%</em>
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Zap size={14} /> Bus Voltage</span>
                      <div>
                        <input
                          type="number"
                          step="1"
                          value={sensors.voltage}
                          onChange={(e) => setSensors({ ...sensors, voltage: Number(e.target.value) })}
                        />
                        <em>V</em>
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Thermometer size={14} /> Ambient Hum</span>
                      <div>
                        <input
                          type="number"
                          step="1"
                          value={sensors.humidity}
                          onChange={(e) => setSensors({ ...sensors, humidity: Number(e.target.value) })}
                        />
                        <em>%</em>
                      </div>
                    </div>
                  </div>

                  <button className="primary-btn full-btn" onClick={runPrediction} disabled={loadingPrediction}>
                    {loadingPrediction ? (
                      <>
                        <RefreshCw size={17} className="spin" /> Analyzing Model Telemetry...
                      </>
                    ) : (
                      <>
                        <BrainCircuit size={17} /> Execute AI Health & RUL Analysis
                      </>
                    )}
                  </button>
                </div>

                {/* Intelligent Maintenance Queue */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <h2>Intelligent Maintenance Queue</h2>
                      <p>AI-prioritized service work orders</p>
                    </div>
                    <button className="text-btn" onClick={() => setActiveTab("Maintenance Queue")}>
                      View All ({workOrders.length})
                    </button>
                  </div>

                  <div>
                    {workOrders.slice(0, 4).map((wo) => (
                      <div className="maintenance-item" key={wo.id}>
                        <div className="maint-machine">{wo.machineId}</div>
                        <div className="maint-info">
                          <b>{wo.title}</b>
                          <span>Assigned: {wo.technician} · {wo.date}</span>
                        </div>
                        <span className={`priority-pill ${wo.priority.toLowerCase()}`}>
                          {wo.priority}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              {/* AI Activity / Recent History */}
              <section className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Recent AI Inference Logs</h2>
                    <p>Live telemetry event log recorded by the predictive maintenance ensemble</p>
                  </div>
                  <button className="text-btn" onClick={fetchBackendData}>
                    <RefreshCw size={14} /> Refresh Log
                  </button>
                </div>

                <div className="activity-table">
                  <div className="table-head">
                    <span>Machine ID</span>
                    <span>Health Index</span>
                    <span>Risk Level</span>
                    <span>Diagnostic Finding</span>
                    <span>Logged At</span>
                  </div>

                  {(history.length > 0 ? history.slice(0, 5) : [
                    { machine_id: "M-104", Health_Score: 92, risk: "LOW", reason: "Nominal vibration and temperature envelope", timestamp: "Just now" },
                    { machine_id: "M-087", Health_Score: 76, risk: "MEDIUM", reason: "Thermal gradient approaching threshold", timestamp: "3 min ago" },
                    { machine_id: "M-221", Health_Score: 48, risk: "HIGH", reason: "Elevated bearing vibration harmonics (5.9 mm/s)", timestamp: "7 min ago" },
                    { machine_id: "M-630", Health_Score: 38, risk: "CRITICAL", reason: "Severe pressure fluctuation and seal wear", timestamp: "12 min ago" }
                  ]).map((item, idx) => (
                    <div className="table-row" key={idx}>
                      <span>
                        <b>{item.machine_id || "M-104"}</b>
                        <small style={{ color: "var(--text-muted)" }}>Ensemble Pipeline</small>
                      </span>
                      <span className={`health-text ${healthTone(item.Health_Score ?? item.health_score ?? 85)}`}>
                        {item.Health_Score ?? item.health_score ?? 85}%
                      </span>
                      <span>
                        <span className={`risk-pill ${riskClass(item.risk || item.Risk_Level)}`}>
                          {item.risk || item.Risk_Level || "LOW"}
                        </span>
                      </span>
                      <span className="event-text">{item.reason || "Ensemble inference recorded"}</span>
                      <span className="time-text">
                        {item.timestamp ? String(item.timestamp).replace("T", " ").slice(0, 19) : "Just now"}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}

          {/* TAB: Live Telemetry */}
          {activeTab === "Live Telemetry" && (
            <div className="tab-view">
              <div className="tab-header-banner">
                <h2>Real-Time Fleet Telemetry & Condition Monitoring</h2>
                <p>Continuous edge sensor telemetry stream across all monitored assets</p>
              </div>

              <div className="panel" style={{ marginBottom: 20 }}>
                <div style={{ display: "flex", gap: 14, flexWrap: "wrap", alignItems: "center", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, background: "var(--surface-2)", padding: "8px 14px", borderRadius: 10, flex: "1 1 300px" }}>
                    <Search size={16} style={{ color: "var(--text-muted)" }} />
                    <input
                      type="text"
                      placeholder="Search by Machine ID, Name, or Production Area..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      style={{ border: 0, outline: 0, background: "transparent", color: "var(--text)", width: "100%", fontSize: 13 }}
                    />
                  </div>

                  <div style={{ display: "flex", gap: 8 }}>
                    {["ALL", "HIGH", "MEDIUM", "LOW"].map((level) => (
                      <button
                        key={level}
                        className={`preset-chip ${filterRisk === level ? "active" : ""}`}
                        style={{
                          background: filterRisk === level ? "var(--primary)" : "var(--surface-2)",
                          color: filterRisk === level ? "#fff" : "var(--text)",
                          borderColor: filterRisk === level ? "var(--primary)" : "var(--border)"
                        }}
                        onClick={() => setFilterRisk(level)}
                      >
                        {level === "ALL" ? "All Assets" : `${level} Risk`}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="panel">
                <div className="activity-table">
                  <div className="table-head" style={{ gridTemplateColumns: "1.2fr 1fr 0.8fr 1fr 1fr 1fr 1fr" }}>
                    <span>Machine Asset</span>
                    <span>Production Area</span>
                    <span>Health Index</span>
                    <span>Risk Status</span>
                    <span>Core Temp</span>
                    <span>Vibration RMS</span>
                    <span>Est. RUL</span>
                  </div>

                  {filteredMachines.map((m) => (
                    <div
                      className="table-row"
                      style={{ gridTemplateColumns: "1.2fr 1fr 0.8fr 1fr 1fr 1fr 1fr", cursor: "pointer" }}
                      key={m.id}
                      onClick={() => {
                        handleSelectMachine(m);
                        setToastMessage(`Loaded ${m.id} (${m.name}) into Diagnostic Lab.`);
                      }}
                    >
                      <span>
                        <b>{m.id}</b>
                        <small style={{ color: "var(--text-muted)" }}>{m.name}</small>
                      </span>
                      <span>{m.area}</span>
                      <span className={`health-text ${healthTone(m.health)}`}>{m.health}%</span>
                      <span>
                        <span className={`risk-pill ${riskClass(m.risk)}`}>{m.risk}</span>
                      </span>
                      <span>{m.temp}°C</span>
                      <span>{m.vibration} mm/s</span>
                      <span style={{ fontWeight: 600 }}>{m.rul} Hours</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB: AI Diagnostics */}
          {activeTab === "AI Diagnostics" && (
            <div className="tab-view">
              <div className="tab-header-banner">
                <h2>AI Diagnostics & Stress Testing Laboratory</h2>
                <p>Simulate industrial stress anomalies and inspect explainable feature contributions</p>
              </div>

              <div className="section-grid detail-grid">
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <h2>Diagnostic Target: {selectedMachine.id}</h2>
                      <p>{selectedMachine.name} · {selectedMachine.area}</p>
                    </div>
                  </div>

                  <div className="sensor-presets">
                    <button className="preset-chip" onClick={() => applyPreset("optimal")}>✓ Nominal</button>
                    <button className="preset-chip" onClick={() => applyPreset("thermal")}>🔥 Thermal Overheat</button>
                    <button className="preset-chip" onClick={() => applyPreset("bearing")}>⚠️ Bearing Wear</button>
                    <button className="preset-chip" onClick={() => applyPreset("critical")}>🚨 Critical Runout</button>
                  </div>

                  <div className="sensor-grid" style={{ gridTemplateColumns: "repeat(2, 1fr)", marginTop: 14 }}>
                    <div className="sensor-input">
                      <span><Thermometer size={14} /> Temperature (°C)</span>
                      <div>
                        <input
                          type="number"
                          step="0.5"
                          value={sensors.temperature}
                          onChange={(e) => setSensors({ ...sensors, temperature: Number(e.target.value) })}
                        />
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Activity size={14} /> Vibration (mm/s)</span>
                      <div>
                        <input
                          type="number"
                          step="0.1"
                          value={sensors.vibration}
                          onChange={(e) => setSensors({ ...sensors, vibration: Number(e.target.value) })}
                        />
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Gauge size={14} /> Hydraulic Pressure (bar)</span>
                      <div>
                        <input
                          type="number"
                          step="0.1"
                          value={sensors.pressure}
                          onChange={(e) => setSensors({ ...sensors, pressure: Number(e.target.value) })}
                        />
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Zap size={14} /> Motor Current (A)</span>
                      <div>
                        <input
                          type="number"
                          step="0.1"
                          value={sensors.motor_current}
                          onChange={(e) => setSensors({ ...sensors, motor_current: Number(e.target.value) })}
                        />
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Activity size={14} /> Shaft RPM</span>
                      <div>
                        <input
                          type="number"
                          step="10"
                          value={sensors.rpm}
                          onChange={(e) => setSensors({ ...sensors, rpm: Number(e.target.value) })}
                        />
                      </div>
                    </div>

                    <div className="sensor-input">
                      <span><Gauge size={14} /> Mechanical Load (%)</span>
                      <div>
                        <input
                          type="number"
                          step="1"
                          value={sensors.load_percentage}
                          onChange={(e) => setSensors({ ...sensors, load_percentage: Number(e.target.value) })}
                        />
                      </div>
                    </div>
                  </div>

                  <button className="primary-btn full-btn" onClick={runPrediction} disabled={loadingPrediction}>
                    {loadingPrediction ? "Analyzing..." : "Compute Health Index & SHAP Decomposition"}
                  </button>
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <h2>Diagnostic Projection</h2>
                      <p>Model output metrics based on active inputs</p>
                    </div>
                  </div>

                  <div style={{ textAlign: "center", padding: "10px 0 20px" }}>
                    <div style={{ fontSize: 52, fontFamily: "Space Grotesk", fontWeight: 700 }}>
                      {selectedMachine.health}%
                    </div>
                    <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
                      Health Score Evaluation
                    </div>
                    <span className={`risk-pill ${riskClass(selectedMachine.risk)}`} style={{ marginTop: 10 }}>
                      {selectedMachine.risk} RISK
                    </span>
                  </div>

                  <div className="explain-intro">
                    <Sparkles size={14} /> Primary Root Cause: <b>{selectedMachine.component}</b>
                  </div>

                  {shapContributions.map((s) => (
                    <div className="feature-row" key={s.label}>
                      <div>
                        <span>{s.label}</span>
                        <b>{s.value}%</b>
                      </div>
                      <div className="feature-track">
                        <i style={{ width: `${s.value}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB: Maintenance Queue */}
          {activeTab === "Maintenance Queue" && (
            <div className="tab-view">
              <div className="tab-header-banner">
                <h2>Intelligent Maintenance Dispatch Queue</h2>
                <p>AI-scheduled preventive work orders, priority triage, and technician allocation</p>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Active Service Work Orders</h2>
                    <p>Total {workOrders.length} work orders in system queue</p>
                  </div>
                  <button
                    className="primary-btn"
                    onClick={() => {
                      const newId = `WO-${Math.floor(8000 + Math.random() * 999)}`;
                      setWorkOrders([
                        {
                          id: newId,
                          machineId: selectedMachine.id,
                          title: `Inspection for ${selectedMachine.component} wear`,
                          priority: selectedMachine.risk === "CRITICAL" ? "Critical" : selectedMachine.risk === "HIGH" ? "Critical" : "Medium",
                          status: "Scheduled",
                          technician: "Sandeep S",
                          date: "Today"
                        },
                        ...workOrders
                      ]);
                      setToastMessage(`Dispatched new work order ${newId} for ${selectedMachine.id}`);
                    }}
                  >
                    <Wrench size={15} /> Create Work Order for {selectedMachine.id}
                  </button>
                </div>

                <div className="activity-table">
                  <div className="table-head" style={{ gridTemplateColumns: "1fr 1fr 2fr 1fr 1fr 1fr" }}>
                    <span>Order ID</span>
                    <span>Machine ID</span>
                    <span>Action Brief</span>
                    <span>Priority</span>
                    <span>Technician</span>
                    <span>Status</span>
                  </div>

                  {workOrders.map((wo) => (
                    <div className="table-row" style={{ gridTemplateColumns: "1fr 1fr 2fr 1fr 1fr 1fr" }} key={wo.id}>
                      <b>{wo.id}</b>
                      <span>{wo.machineId}</span>
                      <span>{wo.title}</span>
                      <span>
                        <span className={`priority-pill ${wo.priority.toLowerCase()}`}>
                          {wo.priority}
                        </span>
                      </span>
                      <span>{wo.technician}</span>
                      <span>
                        <button
                          className="preset-chip"
                          onClick={() => {
                            setWorkOrders(workOrders.map(w => w.id === wo.id ? { ...w, status: w.status === "Completed" ? "Pending" : "Completed" } : w));
                            setToastMessage(`Updated status for ${wo.id}`);
                          }}
                        >
                          {wo.status}
                        </button>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB: ML Architecture */}
          {activeTab === "ML Architecture" && (
            <div className="tab-view">
              <div className="tab-header-banner">
                <h2>Predictive Maintenance Multi-Model Architecture</h2>
                <p>Ensemble AI incorporating supervised classifiers, regressors, and deep anomaly detection</p>
              </div>

              <div className="model-cards-grid">
                <div className="model-card-item">
                  <div className="model-card-item-top">
                    <span className="model-chip">Ensemble Classifier</span>
                    <ShieldCheck size={18} style={{ color: "var(--success)" }} />
                  </div>
                  <h3>Random Forest Classifier</h3>
                  <p>Aggregates 180 decision trees with balanced class weighting to categorize machine failure probability.</p>
                  <div className="model-metrics-row">
                    <div>
                      <small>Accuracy</small>
                      <strong>94.2%</strong>
                    </div>
                    <div>
                      <small>F1-Score</small>
                      <strong>0.93</strong>
                    </div>
                    <div>
                      <small>Latency</small>
                      <strong>12 ms</strong>
                    </div>
                  </div>
                </div>

                <div className="model-card-item">
                  <div className="model-card-item-top">
                    <span className="model-chip">Gradient Boosting</span>
                    <ShieldCheck size={18} style={{ color: "var(--success)" }} />
                  </div>
                  <h3>XGBoost Regressor</h3>
                  <p>Calculates Remaining Useful Life (RUL) estimation with second-order gradient optimizations.</p>
                  <div className="model-metrics-row">
                    <div>
                      <small>MAE</small>
                      <strong>4.8 hrs</strong>
                    </div>
                    <div>
                      <small>R² Score</small>
                      <strong>0.91</strong>
                    </div>
                    <div>
                      <small>Latency</small>
                      <strong>18 ms</strong>
                    </div>
                  </div>
                </div>

                <div className="model-card-item">
                  <div className="model-card-item-top">
                    <span className="model-chip">Unsupervised Anomaly</span>
                    <ShieldCheck size={18} style={{ color: "var(--success)" }} />
                  </div>
                  <h3>Isolation Forest</h3>
                  <p>Partitions multivariate sensor spaces to isolate rare failure signatures before catastrophic breakdown.</p>
                  <div className="model-metrics-row">
                    <div>
                      <small>Contamination</small>
                      <strong>0.05</strong>
                    </div>
                    <div>
                      <small>ROC-AUC</small>
                      <strong>0.96</strong>
                    </div>
                    <div>
                      <small>Latency</small>
                      <strong>8 ms</strong>
                    </div>
                  </div>
                </div>

                <div className="model-card-item">
                  <div className="model-card-item-top">
                    <span className="model-chip">Deep Sequence</span>
                    <ShieldCheck size={18} style={{ color: "var(--success)" }} />
                  </div>
                  <h3>LSTM Neural Network</h3>
                  <p>Captures temporal degradation dependencies across time-series vibration and temperature cycles.</p>
                  <div className="model-metrics-row">
                    <div>
                      <small>Seq Length</small>
                      <strong>50 steps</strong>
                    </div>
                    <div>
                      <small>Precision</small>
                      <strong>93.4%</strong>
                    </div>
                    <div>
                      <small>Latency</small>
                      <strong>24 ms</strong>
                    </div>
                  </div>
                </div>

                <div className="model-card-item">
                  <div className="model-card-item-top">
                    <span className="model-chip">Reconstruction Model</span>
                    <ShieldCheck size={18} style={{ color: "var(--success)" }} />
                  </div>
                  <h3>Autoencoder Network</h3>
                  <p>Calculates reconstruction error on sensor telemetry vectors to detect anomalous sensor drift.</p>
                  <div className="model-metrics-row">
                    <div>
                      <small>MSE Loss</small>
                      <strong>0.003</strong>
                    </div>
                    <div>
                      <small>Recall</small>
                      <strong>95.8%</strong>
                    </div>
                    <div>
                      <small>Latency</small>
                      <strong>14 ms</strong>
                    </div>
                  </div>
                </div>

                <div className="model-card-item">
                  <div className="model-card-item-top">
                    <span className="model-chip">Explainable AI</span>
                    <ShieldCheck size={18} style={{ color: "var(--success)" }} />
                  </div>
                  <h3>SHAP TreeExplainer</h3>
                  <p>Provides exact Shapley values to diagnose the exact physical causes behind every model decision.</p>
                  <div className="model-metrics-row">
                    <div>
                      <small>Coverage</small>
                      <strong>100%</strong>
                    </div>
                    <div>
                      <small>Explainability</small>
                      <strong>Exact</strong>
                    </div>
                    <div>
                      <small>Latency</small>
                      <strong>22 ms</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Footer */}
          <footer>
            <div>
              <div className="footer-logo">
                <BrainCircuit size={18} />
              </div>
              <div>
                <strong>Maintaina Industrial Platform</strong>
                <span style={{ display: "block", fontSize: 11, color: "var(--text-muted)" }}>
                  Random Forest · XGBoost · Isolation Forest · LSTM · Autoencoder
                </span>
              </div>
            </div>
            <div>
              <span>Predictive Maintenance Intelligence Suite © 2026</span>
            </div>
          </footer>
        </div>
      </main>

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="toast">
          <CheckCircle2 size={18} style={{ color: "var(--success)" }} />
          <span>{toastMessage}</span>
          <button onClick={() => setToastMessage("")}>
            <X size={15} />
          </button>
        </div>
      )}
    </div>
  );
}

function intVal(num) {
  return Math.round(Number(num) || 0);
}
