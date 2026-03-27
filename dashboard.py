"""
RoadVolt – Smart City Energy Dashboard
Run with:  streamlit run dashboard.py
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

# ─────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="RoadVolt  Dashboard",
    page_icon="⚡",
    layout=" wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
#  Auto Refresh (every 5 seconds)
# ─────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="autorefresh")
except ImportError:
    pass

# ─────────────────────────────────────────
#  Custom CSS – Premium Redesign
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

/* ══════════════════════════════════════
   GLOBAL RESET & BASE
══════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg-primary:    #020917;
    --bg-secondary:  #050f1f;
    --bg-card:       rgba(8, 20, 45, 0.85);
    --bg-card-hover: rgba(10, 26, 56, 0.95);
    --border-dim:    rgba(0, 180, 255, 0.12);
    --border-bright: rgba(0, 220, 255, 0.35);
    --neon-cyan:     #00e5ff;
    --neon-blue:     #0080ff;
    --neon-green:    #00ffaa;
    --neon-orange:   #ff7b2e;
    --neon-gold:     #ffd060;
    --text-primary:  #e8f4ff;
    --text-secondary:#6b9ec7;
    --text-dim:      #2d5278;
    --shadow-cyan:   0 0 30px rgba(0, 229, 255, 0.12);
    --shadow-glow:   0 0 60px rgba(0, 128, 255, 0.08);
    --radius-sm:     8px;
    --radius-md:     14px;
    --radius-lg:     20px;
    --radius-xl:     28px;
}

/* Page background with animated mesh */
.stApp {
    background: 
        radial-gradient(ellipse at 20% 20%, rgba(0, 100, 200, 0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(0, 200, 150, 0.04) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 0%, rgba(0, 60, 150, 0.08) 0%, transparent 60%),
        linear-gradient(170deg, #020917 0%, #030c1a 40%, #020813 100%);
    min-height: 100vh;
}

/* Streamlit overrides */
.block-container {
    padding: 1.2rem 2rem 2rem !important;
    max-width: 1600px !important;
}
.stApp > header { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] > div { background: rgba(2, 8, 20, 0.96) !important; }
section[data-testid="stSidebar"] {
    border-right: 1px solid var(--border-dim) !important;
}
div[data-testid="metric-container"] > div { background: transparent !important; }
.stMetric { color: var(--text-primary); }
.stCheckbox label { color: var(--text-secondary) !important; font-family: 'Rajdhani', sans-serif !important; }
.stButton > button {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
}
div[data-testid="stHorizontalBlock"] { gap: 1rem !important; }

/* ══════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

/* ══════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════ */
.main-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.6rem, 3vw, 2.6rem);
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #00e5ff 0%, #0088ff 40%, #00ffaa 80%, #00e5ff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 4px;
    text-transform: uppercase;
    animation: shimmer 4s linear infinite;
    filter: drop-shadow(0 0 20px rgba(0,229,255,0.3));
}

@keyframes shimmer {
    0%   { background-position: 0% center; }
    100% { background-position: 200% center; }
}

.sub-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.78rem;
    text-align: center;
    color: var(--text-dim);
    letter-spacing: 5px;
    text-transform: uppercase;
    margin-top: 4px;
}

.live-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-secondary);
    letter-spacing: 1px;
    padding: 8px 0;
}

.live-dot {
    width: 7px; height: 7px;
    background: var(--neon-green);
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px var(--neon-green), 0 0 14px rgba(0,255,170,0.4);
    animation: pulse-dot 1.5s ease-in-out infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.6; transform: scale(0.85); }
}

/* ══════════════════════════════════════
   DIVIDERS
══════════════════════════════════════ */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-dim) 30%, var(--border-bright) 50%, var(--border-dim) 70%, transparent) !important;
    margin: 1.5rem 0 !important;
}

/* ══════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════ */
.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--neon-cyan);
    letter-spacing: 4px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.8rem 0 1rem;
    opacity: 0.9;
}

.section-header::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 16px;
    background: linear-gradient(180deg, var(--neon-cyan), var(--neon-blue));
    border-radius: 2px;
    box-shadow: 0 0 8px var(--neon-cyan);
    flex-shrink: 0;
}

.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-bright), transparent);
    margin-left: 8px;
}

/* ══════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════ */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-dim);
    border-radius: var(--radius-lg);
    padding: 18px 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.metric-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(0,229,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}

.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,255,0.4), transparent);
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: var(--border-bright);
    box-shadow: var(--shadow-cyan), 0 8px 32px rgba(0,0,0,0.4);
}

.metric-icon {
    font-size: 1.3rem;
    margin-bottom: 4px;
    filter: drop-shadow(0 0 6px rgba(0,229,255,0.5));
}

.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--neon-cyan);
    line-height: 1.1;
    text-shadow: 0 0 20px rgba(0,229,255,0.4);
}

.metric-unit {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-secondary);
    margin-top: 2px;
    opacity: 0.7;
}

/* ══════════════════════════════════════
   ALERT STYLES
══════════════════════════════════════ */
.alert-wrap {
    border-radius: var(--radius-md);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    position: relative;
    overflow: hidden;
}

.alert-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background: inherit;
    filter: blur(0);
    z-index: -1;
}

.alert-green {
    background: rgba(0, 255, 140, 0.06);
    border: 1px solid rgba(0, 255, 140, 0.3);
    color: var(--neon-green);
    box-shadow: 0 0 20px rgba(0,255,140,0.08);
}
.alert-yellow {
    background: rgba(255, 208, 96, 0.06);
    border: 1px solid rgba(255, 208, 96, 0.3);
    color: var(--neon-gold);
    box-shadow: 0 0 20px rgba(255,208,96,0.08);
}
.alert-red {
    background: rgba(255, 80, 80, 0.07);
    border: 1px solid rgba(255, 80, 80, 0.3);
    color: #ff6060;
    box-shadow: 0 0 20px rgba(255,80,80,0.08);
    animation: alert-pulse 2s ease-in-out infinite;
}

@keyframes alert-pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(255,80,80,0.08); }
    50%       { box-shadow: 0 0 30px rgba(255,80,80,0.2); }
}

.alert-indicator {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.ind-green  { background: var(--neon-green); box-shadow: 0 0 8px var(--neon-green); }
.ind-yellow { background: var(--neon-gold);  box-shadow: 0 0 8px var(--neon-gold); animation: pulse-dot 1.5s ease-in-out infinite; }
.ind-red    { background: #ff6060;            box-shadow: 0 0 8px #ff6060;          animation: pulse-dot 0.8s ease-in-out infinite; }

/* ══════════════════════════════════════
   AI INSIGHT CARDS
══════════════════════════════════════ */
.ai-metric-card {
    background: rgba(5, 14, 32, 0.9);
    border: 1px solid var(--border-dim);
    border-radius: var(--radius-sm);
    padding: 11px 16px;
    margin-bottom: 7px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: border-color 0.2s, background 0.2s;
    backdrop-filter: blur(8px);
}
.ai-metric-card:hover {
    border-color: rgba(0, 229, 255, 0.25);
    background: rgba(8, 22, 50, 0.95);
}
.ai-metric-label {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-secondary);
    font-size: 0.78rem;
    letter-spacing: 1px;
}
.ai-metric-value {
    font-family: 'Orbitron', monospace;
    color: var(--neon-cyan);
    font-size: 0.82rem;
    font-weight: 600;
}

/* ══════════════════════════════════════
   AI MODULE HEADER
══════════════════════════════════════ */
.ai-module-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 128, 255, 0.1);
    border: 1px solid rgba(0, 128, 255, 0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--neon-blue);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* ══════════════════════════════════════
   SMART CITY INSIGHT CARDS
══════════════════════════════════════ */
.insight-card {
    background: var(--bg-card);
    border: 1px solid var(--border-dim);
    border-radius: var(--radius-lg);
    padding: 22px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
    backdrop-filter: blur(10px);
}
.insight-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,255,170,0.5), transparent);
}
.insight-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0,255,170,0.25);
    box-shadow: 0 0 25px rgba(0,255,170,0.08);
}
.insight-icon { font-size: 1.6rem; margin-bottom: 6px; }
.insight-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.insight-value {
    font-family: 'Orbitron', monospace;
    color: var(--neon-green);
    font-size: 1.4rem;
    font-weight: 700;
    text-shadow: 0 0 16px rgba(0,255,170,0.35);
}
.insight-sub {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-secondary);
    font-size: 0.72rem;
    margin-top: 2px;
    opacity: 0.8;
}

/* ══════════════════════════════════════
   BATTERY DISPLAY
══════════════════════════════════════ */
.battery-card {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    padding: 26px 24px;
    text-align: center;
    height: 100%;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.battery-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.battery-value {
    font-family: 'Orbitron', monospace;
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 6px;
}
.battery-status {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 2px;
    margin-bottom: 16px;
}
.battery-bar-bg {
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    height: 8px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}
.battery-bar-fill {
    height: 100%;
    border-radius: 20px;
    transition: width 0.6s ease;
    position: relative;
}
.battery-bar-fill::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 20px; height: 100%;
    background: rgba(255,255,255,0.3);
    border-radius: 20px;
    filter: blur(4px);
}

/* ══════════════════════════════════════
   SDG BADGES
══════════════════════════════════════ */
.sdg-wrap {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 1rem 0;
}
.sdg-label {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-dim);
    letter-spacing: 2px;
    font-size: 0.7rem;
    text-transform: uppercase;
    margin-right: 4px;
}
.sdg-badge {
    padding: 5px 14px;
    border-radius: 20px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
    border: 1px solid rgba(255,255,255,0.15);
}

/* ══════════════════════════════════════
   SIDEBAR
══════════════════════════════════════ */
.sidebar-logo {
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    font-weight: 900;
    color: var(--neon-cyan);
    letter-spacing: 3px;
    text-align: center;
    padding: 14px 0 4px;
    text-shadow: 0 0 20px rgba(0,229,255,0.4);
}
.sidebar-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 4px;
    text-align: center;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.sidebar-stat {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-dim);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.sidebar-stat-label {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-secondary);
    font-size: 0.78rem;
    letter-spacing: 1px;
}
.sidebar-stat-value {
    font-family: 'Orbitron', monospace;
    color: var(--neon-cyan);
    font-size: 0.85rem;
    font-weight: 600;
}
.sidebar-footer {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    color: var(--text-dim);
    text-align: center;
    letter-spacing: 1.5px;
    line-height: 1.6;
    padding: 12px 0;
}

/* ══════════════════════════════════════
   REFRESH BUTTON
══════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,128,255,0.15), rgba(0,229,255,0.08)) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--neon-cyan) !important;
    border-radius: var(--radius-sm) !important;
    padding: 8px 20px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,128,255,0.25), rgba(0,229,255,0.15)) !important;
    box-shadow: 0 0 16px rgba(0,229,255,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ══════════════════════════════════════
   DATAFRAME
══════════════════════════════════════ */
.stDataFrame {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}

/* ══════════════════════════════════════
   PLOTLY CHART CONTAINERS
══════════════════════════════════════ */
.chart-container {
    background: rgba(5, 14, 32, 0.7);
    border: 1px solid var(--border-dim);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: border-color 0.2s ease;
}
.chart-container:hover { border-color: var(--border-bright); }

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.dashboard-footer {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: var(--text-dim);
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════
   CHART WRAPPER
══════════════════════════════════════ */
div[data-testid="stPlotlyChart"] {
    background: rgba(5, 14, 32, 0.6);
    border: 1px solid var(--border-dim);
    border-radius: var(--radius-md);
    overflow:   hidden;
    padding:  2px;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
div[data-testid="stPlotlyChart"]:hover {
    border-color: rgba(0,229,255,0.22);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  Database Connection
# ─────────────────────────────────────────
@st.cache_resource
def get_connection():
    return sqlite3.connect("energy.db", check_same_thread=False)

conn = get_connection()


def load_data():
    try:
        df = pd.read_sql("SELECT * FROM energy_data ORDER BY id ASC", conn)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        # Demo data when no real data exists
        n = 30
        df = pd.DataFrame({
            "id": range(1, n+1),
            "voltage": np.random.uniform(10, 14, n).round(2),
            "current": np.random.uniform(0.3, 0.9, n).round(3),
            "power": np.random.uniform(3.5, 12, n).round(3),
            "vehicle": np.random.randint(0, 3, n),
            "battery": np.linspace(40, 78, n).round(1),
            "timestamp": pd.date_range("2026-03-09 08:00", periods=n, freq="2min")
        })
        df["timestamp"] = df["timestamp"].astype(str)
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ─────────────────────────────────────────
#  Load Data
# ─────────────────────────────────────────
df = load_data()

# ─────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">⚡ ROADVOLT</div>
    <div class="sidebar-sub">Smart Energy System</div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    total_vehicles = int(df["vehicle"].sum())
    total_energy   = round(df["power"].sum() / 1000, 3)
    uptime_hrs     = round(len(df) * 5 / 3600, 1)

    sidebar_stats = [
        ("🚗 Total Vehicles",  f"{total_vehicles:,}"),
        ("⚡ Energy",          f"{total_energy} kWh"),
        ("📊 Data Points",     f"{len(df)}"),
    ]
    for label, value in sidebar_stats:
        st.markdown(f"""
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">{label}</span>
            <span class="sidebar-stat-value">{value}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    show_raw = st.checkbox("Show Raw Data Table", value=False)
    show_ai  = st.checkbox("Show AI Prediction",  value=True)
    st.markdown("<br>", unsafe_allow_html=True)
    refresh  = st.button("⟳  Refresh Now")

    st.markdown("---")
    st.markdown("""
    <div class="sidebar-footer">
        SDG 7 · SDG 9 · SDG 11 · SDG 13<br>
        <span style='color:rgba(0,229,255,0.6)'>Smart Infrastructure Project</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
#  Header
# ─────────────────────────────────────────
st.markdown('<div class="main-title">⚡ RoadVolt Smart Energy System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Smart Speed Breaker · IoT Monitoring · AI Analytics · Smart City Dashboard</div>', unsafe_allow_html=True)

# Live status bar
st.markdown(f"""
<div class="live-status">
    <span><span class="live-dot"></span></span>
    <span>LIVE MONITORING</span>
    <span style="color:rgba(107,158,199,0.4)">|</span>
    <span>{datetime.now().strftime('%H:%M:%S')}</span>
    <span style="color:rgba(107,158,199,0.4)">|</span>
    <span>{len(df)} RECORDS</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Live Metric Cards
# ─────────────────────────────────────────
voltage  = round(float(df["voltage"].iloc[-1]),  2)
current  = round(float(df["current"].iloc[-1]),  3)
power    = round(float(df["power"].iloc[-1]),    3)
battery  = round(float(df["battery"].iloc[-1]),  1)
vehicles = int(df["vehicle"].sum())
energy_per_v = round(df["power"].sum() / max(vehicles, 1), 3)

col1, col2, col3, col4, col5, col6 = st.columns(6)

cards = [
    (col1, "⚡", "Voltage",           f"{voltage}",      "V"),
    (col2, "🔌", "Current",           f"{current}",      "A"),
    (col3, "💡", "Power",             f"{power}",        "W"),
    (col4, "🔋", "Battery",           f"{battery}",      "%"),
    (col5, "🚗", "Total Vehicles",    f"{vehicles:,}",   "count"),
    (col6, "📊", "Energy / Vehicle",  f"{energy_per_v}", "Wh"),
]

for col, icon, label, value, unit in cards:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-unit">{unit}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Traffic Density Alert
# ─────────────────────────────────────────
recent_vehicles = int(df["vehicle"].tail(5).sum())
if recent_vehicles >= 8:
    alert_class = "alert-red"
    ind_class   = "ind-red"
    alert_msg   = "HIGH TRAFFIC DENSITY DETECTED — Peak Energy Generation Mode Active"
    alert_icon  = "🚨"
elif recent_vehicles >= 4:
    alert_class = "alert-yellow"
    ind_class   = "ind-yellow"
    alert_msg   = "MODERATE TRAFFIC — Normal Energy Harvesting in Progress"
    alert_icon  = "⚠️"
else:
    alert_class = "alert-green"
    ind_class   = "ind-green"
    alert_msg   = "LOW TRAFFIC — System Standby / Normal Operation"
    alert_icon  = "✅"

st.markdown(f"""
<div class="alert-wrap {alert_class}">
    <span class="alert-indicator {ind_class}"></span>
    <span>{alert_icon}&nbsp;&nbsp;{alert_msg}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────
#  Gauge Charts
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Energy Monitoring Gauges</div>', unsafe_allow_html=True)

def make_gauge(title, value, max_val, color_start, color_end, suffix=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={
            "suffix": suffix,
            "font": {"size": 26, "color": color_end, "family": "Orbitron"}
        },
        title={
            "text": title,
            "font": {"size": 11, "color": "#6b9ec7", "family": "Rajdhani"}
        },
        delta={
            "reference": max_val * 0.5,
            "font": {"size": 11, "color": "#6b9ec7"}
        },
        gauge={
            "axis": {
                "range": [0, max_val],
                "tickcolor": "#2d5278",
                "tickfont": {"color": "#2d5278", "size": 9},
                "tickwidth": 1,
                "nticks": 5
            },
            "bar":  {"color": color_end, "thickness": 0.22},
            "bgcolor": "rgba(5,14,32,0)",
            "bordercolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,           max_val * 0.35], "color": "rgba(0,0,0,0.3)"},
                {"range": [max_val*0.35, max_val * 0.65], "color": "rgba(0,60,120,0.2)"},
                {"range": [max_val*0.65, max_val],        "color": "rgba(0,80,160,0.15)"},
            ],
            "threshold": {
                "line": {"color": "#00ffaa", "width": 2},
                "thickness": 0.7,
                "value": max_val * 0.85
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=55, b=10),
        height=210,
        font_color="#ffffff"
    )
    return fig

g1, g2, g3, g4 = st.columns(4)
g1.plotly_chart(make_gauge("VOLTAGE",   voltage,  25,  "#0072ff", "#00e5ff", " V"), use_container_width=True)
g2.plotly_chart(make_gauge("CURRENT",   current,   5,  "#ff6b35", "#ff9a50", " A"), use_container_width=True)
g3.plotly_chart(make_gauge("POWER",     power,    20,  "#00ff88", "#00ffaa", " W"), use_container_width=True)
g4.plotly_chart(make_gauge("BATTERY",   battery, 100,  "#ff3232", "#00ff88", " %"), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
#  Shared Plotly Layout Defaults
# ─────────────────────────────────────────
_CHART_BG   = "rgba(5,14,32,0)"
_PAPER_BG   = "rgba(5,14,32,0)"
_GRID_COLOR = "rgba(0,100,200,0.08)"
_AXIS_COLOR = "#2d5278"
_FONT_COLOR = "#6b9ec7"
_TITLE_FONT = dict(color="#00e5ff", family="Orbitron", size=11)
_AXIS_FONT  = dict(color=_AXIS_COLOR, size=9)

def _base_layout(title_text, height=300):
    return dict(
        title=dict(text=title_text, font=_TITLE_FONT, pad=dict(l=4)),
        paper_bgcolor=_PAPER_BG,
        plot_bgcolor=_CHART_BG,
        font_color=_FONT_COLOR,
        height=height,
        margin=dict(l=10, r=10, t=48, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,100,200,0.15)",
            borderwidth=1,
            font=dict(size=9, color=_FONT_COLOR)
        ),
        xaxis=dict(
            gridcolor=_GRID_COLOR, gridwidth=1,
            zeroline=False, zerolinecolor=_GRID_COLOR,
            tickfont=_AXIS_FONT, linecolor=_AXIS_COLOR
        ),
        yaxis=dict(
            gridcolor=_GRID_COLOR, gridwidth=1,
            zeroline=False, zerolinecolor=_GRID_COLOR,
            tickfont=_AXIS_FONT, linecolor=_AXIS_COLOR
        ),
    )

# ─────────────────────────────────────────
#  Energy & Traffic Analytics
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Energy & Traffic Analytics</div>', unsafe_allow_html=True)

r1c1, r1c2 = st.columns(2)

# Power Generation over time
with r1c1:
    fig_power = go.Figure()
    fig_power.add_trace(go.Scatter(
        y=df["power"],
        mode="lines",
        fill="tozeroy",
        line=dict(color="#00e5ff", width=2),
        fillcolor="rgba(0,229,255,0.05)",
        name="Power (W)"
    ))
    layout = _base_layout("⚡ Power Generation Over Time")
    layout["yaxis"]["title"] = dict(text="Watts", font=_AXIS_FONT)
    fig_power.update_layout(**layout)
    st.plotly_chart(fig_power, use_container_width=True)

# Vehicle Count
with r1c2:
    fig_veh = go.Figure()
    fig_veh.add_trace(go.Bar(
        y=df["vehicle"],
        marker=dict(
            color=df["vehicle"],
            colorscale=[[0, "rgba(0,100,220,0.6)"], [1, "rgba(0,229,255,0.8)"]],
            line=dict(color="rgba(0,229,255,0.3)", width=0.5)
        ),
        name="Vehicles"
    ))
    layout = _base_layout("🚗 Vehicle Traffic Count")
    layout["yaxis"]["title"] = dict(text="Vehicles", font=_AXIS_FONT)
    fig_veh.update_layout(**layout)
    st.plotly_chart(fig_veh, use_container_width=True)

# Voltage & Current Over Time + V vs I scatter
r2c1, r2c2 = st.columns(2)

with r2c1:
    fig_vi = make_subplots(specs=[[{"secondary_y": True}]])
    fig_vi.add_trace(go.Scatter(
        y=df["voltage"], mode="lines",
        line=dict(color="#ff7b2e", width=1.8),
        name="Voltage (V)"
    ), secondary_y=False)
    fig_vi.add_trace(go.Scatter(
        y=df["current"], mode="lines",
        line=dict(color="#00ffaa", width=1.8),
        name="Current (A)"
    ), secondary_y=True)
    layout = _base_layout("📈 Voltage & Current Trends")
    layout["yaxis"]["title"]  = dict(text="Voltage (V)",  font=_AXIS_FONT)
    layout["yaxis2"] = dict(
        title=dict(text="Current (A)", font=_AXIS_FONT),
        gridcolor=_GRID_COLOR, zeroline=False,
        tickfont=_AXIS_FONT, linecolor=_AXIS_COLOR
    )
    fig_vi.update_layout(**layout)
    st.plotly_chart(fig_vi, use_container_width=True)

with r2c2:
    fig_scatter = px.scatter(
        df, x="voltage", y="current",
        color="power",
        color_continuous_scale=[
            [0,   "rgba(0,40,120,0.8)"],
            [0.5, "rgba(0,128,255,0.9)"],
            [1,   "rgba(0,229,255,1.0)"]
        ],
        size="power",
        title="🔬 Voltage vs Current Relationship"
    )
    layout = _base_layout("🔬 Voltage vs Current Relationship")
    layout["xaxis"]["title"] = dict(text="Voltage (V)", font=_AXIS_FONT)
    layout["yaxis"]["title"] = dict(text="Current (A)", font=_AXIS_FONT)
    layout["coloraxis_colorbar"] = dict(
        tickfont=dict(color=_AXIS_COLOR, size=9),
        title=dict(text="W", font=dict(color=_FONT_COLOR, size=9)),
        outlinewidth=0,
        thickness=10,
        len=0.7
    )
    fig_scatter.update_layout(**layout)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
#  AI Prediction Section
# ─────────────────────────────────────────
if show_ai and len(df) >= 5:
    st.markdown('<div class="section-header">🤖 AI Energy Prediction</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ai-module-badge">
        ◈ LINEAR REGRESSION ENGINE · ACTIVE
    </div>
    """, unsafe_allow_html=True)

    ai_c1, ai_c2 = st.columns([2, 1])

    X      = np.arange(len(df)).reshape(-1, 1)
    y_pow  = df["power"].values
    y_veh  = df["vehicle"].cumsum().values

    model_p = LinearRegression().fit(X, y_pow)
    model_v = LinearRegression().fit(X, y_veh)

    future_steps = 10
    X_future = np.arange(len(df), len(df) + future_steps).reshape(-1, 1)
    pred_power   = model_p.predict(X_future)
    pred_vehicle = model_v.predict(X_future)

    with ai_c1:
        fig_ai = go.Figure()
        fig_ai.add_trace(go.Scatter(
            y=y_pow, mode="lines+markers",
            line=dict(color="#00e5ff", width=2),
            marker=dict(size=3, color="#00e5ff"),
            name="Actual Power"
        ))
        fig_ai.add_trace(go.Scatter(
            x=list(range(len(df), len(df)+future_steps)),
            y=pred_power,
            mode="lines+markers",
            line=dict(color="#ff7b2e", width=2, dash="dot"),
            marker=dict(size=6, symbol="diamond", color="#ff7b2e",
                        line=dict(color="#ffaa70", width=1)),
            name="AI Prediction"
        ))
        fig_ai.add_vrect(
            x0=len(df)-0.5, x1=len(df)+future_steps-0.5,
            fillcolor="rgba(255,123,46,0.04)",
            line_width=0,
            annotation_text="FORECAST ZONE",
            annotation_font=dict(color="#ff7b2e", size=9, family="Space Mono")
        )
        layout = _base_layout("⚡ Power Prediction – Next 10 Readings", height=320)
        layout["yaxis"]["title"] = dict(text="Power (W)", font=_AXIS_FONT)
        fig_ai.update_layout(**layout)
        st.plotly_chart(fig_ai, use_container_width=True)

    with ai_c2:
        next_power = round(float(pred_power[0]), 2)
        next_veh   = round(float(pred_vehicle[-1]) - float(pred_vehicle[0]))
        efficiency = round((df["power"].mean() / max(df["power"].max(), 0.001)) * 100, 1)
        trend      = "📈 Increasing" if model_p.coef_[0] > 0 else "📉 Decreasing"

        ai_metrics = [
            ("🤖 Next Power Output",     f"{next_power} W"),
            ("🚗 Est. Vehicles (next)",  f"~{abs(next_veh)}"),
            ("⚡ System Efficiency",     f"{efficiency}%"),
            ("📊 Energy Trend",          trend),
            ("🏆 Peak Power Seen",       f"{round(df['power'].max(), 2)} W"),
            ("📉 Avg Power",             f"{round(df['power'].mean(), 2)} W"),
        ]

        for label, val in ai_metrics:
            st.markdown(f"""
            <div class="ai-metric-card">
                <span class="ai-metric-label">{label}</span>
                <span class="ai-metric-value">{val}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

# ─────────────────────────────────────────
#  Smart City Insights
# ─────────────────────────────────────────
st.markdown('<div class="section-header">🌆 Smart City Insights</div>', unsafe_allow_html=True)

total_energy_kwh = round(df["power"].sum() / 1000, 4)
co2_saved_g      = round(total_energy_kwh * 820, 2)
led_hours        = round(total_energy_kwh * 1000 / 10, 1)
efficiency_score = round((df["power"].mean() / max(df["power"].max(), 0.001)) * 100, 1)

sc1, sc2, sc3, sc4 = st.columns(4)

insight_cards = [
    (sc1, "⚡",  "Total Energy",    f"{total_energy_kwh}",   "kWh Generated"),
    (sc2, "🌱",  "CO₂ Saved",      f"{co2_saved_g}",        "grams avoided"),
    (sc3, "💡",  "LED Hours",       f"{led_hours}",          "hours powered"),
    (sc4, "🏆",  "Efficiency Score",f"{efficiency_score}%",  "system efficiency"),
]

for col, icon, label, value, sub in insight_cards:
    with col:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-icon">{icon}</div>
            <div class="insight-label">{label}</div>
            <div class="insight-value">{value}</div>
            <div class="insight-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# SDG badges
st.markdown("""
<div class="sdg-wrap">
    <span class="sdg-label">Aligned with UN SDGs:</span>
    <span class="sdg-badge" style="background:rgba(252,195,11,0.15);color:#FCC30B;border-color:rgba(252,195,11,0.3);">SDG 7 — Clean Energy</span>
    <span class="sdg-badge" style="background:rgba(253,105,37,0.12);color:#FD9060;border-color:rgba(253,105,37,0.3);">SDG 9 — Innovation</span>
    <span class="sdg-badge" style="background:rgba(253,157,36,0.12);color:#FDB060;border-color:rgba(253,157,36,0.3);">SDG 11 — Sustainable Cities</span>
    <span class="sdg-badge" style="background:rgba(63,126,68,0.15);color:#6dc672;border-color:rgba(63,126,68,0.35);">SDG 13 — Climate Action</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────
#  Battery Monitoring
# ─────────────────────────────────────────
st.markdown('<div class="section-header">🔋 Battery Monitoring</div>', unsafe_allow_html=True)

bat_col1, bat_col2 = st.columns([1, 2])

with bat_col1:
    bat_level  = battery
    if bat_level > 60:
        bat_color  = "#00ffaa"
        bat_status = "🟢 HEALTHY"
    elif bat_level > 30:
        bat_color  = "#ffd060"
        bat_status = "🟡 MODERATE"
    else:
        bat_color  = "#ff6060"
        bat_status = "🔴 LOW"

    st.markdown(f"""
    <div class="battery-card" style="border:1px solid {bat_color}22;">
        <div class="battery-label">Battery Level</div>
        <div class="battery-value" style="color:{bat_color};text-shadow:0 0 24px {bat_color}55;">{bat_level}%</div>
        <div class="battery-status" style="color:{bat_color};">{bat_status}</div>
        <div class="battery-bar-bg">
            <div class="battery-bar-fill" style="width:{bat_level}%;background:linear-gradient(90deg,{bat_color}99,{bat_color});box-shadow:0 0 10px {bat_color}66;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with bat_col2:
    if len(df) > 0 and "battery" in df.columns:
        fig_bat = go.Figure()
        fig_bat.add_trace(go.Scatter(
            y=df["battery"],
            mode="lines",
            fill="tozeroy",
            line=dict(color="#00ffaa", width=2),
            fillcolor="rgba(0,255,170,0.05)",
            name="Battery %"
        ))
        layout = _base_layout("🔋 Battery Level Over Time", height=200)
        layout["yaxis"]["title"] = dict(text="Battery %", font=_AXIS_FONT)
        layout["yaxis"]["range"] = [0, 105]
        fig_bat.update_layout(**layout)
        st.plotly_chart(fig_bat, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
#  Raw Data Table
# ─────────────────────────────────────────
if show_raw:
    st.markdown('<div class="section-header">📋 Raw System Data</div>', unsafe_allow_html=True)
    display_df = df.copy()
    display_df = display_df.sort_values("id", ascending=False).head(50)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=300
    )

# Footer
st.markdown("""
<div class="dashboard-footer">
    ROADVOLT SMART ENERGY SYSTEM &nbsp;·&nbsp; HACKATHON 2026 &nbsp;·&nbsp; ⚡ POWERED BY IoT + AI
</div>
""", unsafe_allow_html=True)