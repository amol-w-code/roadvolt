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
    page_title="RoadVolt Dashboard",
    page_icon="⚡",
    layout="wide",
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
#  Custom CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

/* Page background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 50%, #0a1020 100%);
}

/* Hide default streamlit padding */
.block-container { padding-top: 1rem; padding-bottom: 1rem; }

/* Main title */
.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #00f5ff, #0072ff, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 3px;
    margin-bottom: 0.2rem;
    text-transform: uppercase;
}

.sub-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    text-align: center;
    color: #4a7ab5;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0d1f3c, #112244);
    border: 1px solid #1e3a6e;
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 0 20px rgba(0,114,255,0.15);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); }

.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    color: #4a7ab5;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #00f5ff;
    line-height: 1.2;
}
.metric-unit {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    color: #4a7ab5;
}

/* Section headers */
.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: #00f5ff;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-left: 3px solid #0072ff;
    padding-left: 12px;
    margin: 1.5rem 0 1rem 0;
}

/* Alert boxes */
.alert-green {
    background: rgba(0,255,136,0.1);
    border: 1px solid #00ff88;
    border-radius: 10px;
    padding: 12px 18px;
    color: #00ff88;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    letter-spacing: 1px;
}
.alert-yellow {
    background: rgba(255,200,0,0.1);
    border: 1px solid #ffc800;
    border-radius: 10px;
    padding: 12px 18px;
    color: #ffc800;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    letter-spacing: 1px;
}
.alert-red {
    background: rgba(255,50,50,0.1);
    border: 1px solid #ff3232;
    border-radius: 10px;
    padding: 12px 18px;
    color: #ff3232;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    letter-spacing: 1px;
}

/* Dataframe */
.stDataFrame { border-radius: 12px; }

/* Sidebar */
.css-1d391kg { background: #0a0e1a; }

/* Divider */
hr { border-color: #1e3a6e !important; }
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
    <div style='font-family:Orbitron;font-size:1.1rem;color:#00f5ff;
                letter-spacing:2px;text-align:center;padding:10px 0;'>
        ⚡ ROADVOLT
    </div>
    <div style='font-family:Rajdhani;font-size:0.8rem;color:#4a7ab5;
                letter-spacing:3px;text-align:center;margin-bottom:1.5rem;'>
        SMART ENERGY SYSTEM
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    total_vehicles = int(df["vehicle"].sum())
    total_energy   = round(df["power"].sum() / 1000, 3)
    uptime_hrs     = round(len(df) * 5 / 3600, 1)

    st.metric("🚗 Total Vehicles",  f"{total_vehicles:,}")
    st.metric("⚡ Energy (kWh)",    f"{total_energy}")
    st.metric("🕐 Data Points",     f"{len(df)}")
    st.markdown("---")

    show_raw = st.checkbox("Show Raw Data Table", value=False)
    show_ai  = st.checkbox("Show AI Prediction",  value=True)
    refresh  = st.button("🔄 Refresh Now")

    st.markdown("---")
    st.markdown("""
    <div style='font-family:Rajdhani;font-size:0.8rem;color:#4a7ab5;text-align:center;'>
        SDG 7 · SDG 9 · SDG 11 · SDG 13<br>
        <span style='color:#00f5ff'>Smart Infrastructure Project</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
#  Header
# ─────────────────────────────────────────
st.markdown('<div class="main-title">⚡ RoadVolt Smart Energy System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Smart Speed Breaker · IoT Monitoring · AI Analytics · Smart City Dashboard</div>', unsafe_allow_html=True)

# Live timestamp
st.markdown(
    f"<div style='text-align:center;font-family:Rajdhani;color:#4a7ab5;"
    f"font-size:0.85rem;margin-bottom:1rem;'>"
    f"🟢 LIVE  ·  Last Updated: {datetime.now().strftime('%H:%M:%S')}  ·  "
    f"Records: {len(df)}</div>",
    unsafe_allow_html=True
)

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
            <div style="font-size:1.6rem">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-unit">{unit}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Traffic Density Alert
# ─────────────────────────────────────────
recent_vehicles = int(df["vehicle"].tail(5).sum())
if recent_vehicles >= 8:
    alert_class = "alert-red"
    alert_msg   = "🚨 HIGH TRAFFIC DENSITY DETECTED — Peak Energy Generation Mode Active"
elif recent_vehicles >= 4:
    alert_class = "alert-yellow"
    alert_msg   = "⚠️ MODERATE TRAFFIC — Normal Energy Harvesting in Progress"
else:
    alert_class = "alert-green"
    alert_msg   = "✅ LOW TRAFFIC — System Standby / Normal Operation"

st.markdown(f'<div class="{alert_class}">{alert_msg}</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Gauge Charts
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Energy Monitoring Gauges</div>', unsafe_allow_html=True)

def make_gauge(title, value, max_val, color_start, color_end, suffix=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={"suffix": suffix, "font": {"size": 28, "color": "#00f5ff", "family": "Orbitron"}},
        title={"text": title, "font": {"size": 14, "color": "#4a7ab5", "family": "Rajdhani"}},
        delta={"reference": max_val * 0.5, "font": {"size": 12}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#4a7ab5",
                     "tickfont": {"color": "#4a7ab5", "size": 10}},
            "bar":  {"color": color_end, "thickness": 0.25},
            "bgcolor": "#0d1526",
            "bordercolor": "#1e3a6e",
            "steps": [
                {"range": [0,           max_val * 0.4], "color": "#0d1f3c"},
                {"range": [max_val*0.4, max_val * 0.7], "color": "#112244"},
                {"range": [max_val*0.7, max_val],       "color": "#1a3060"},
            ],
            "threshold": {
                "line": {"color": "#00ff88", "width": 3},
                "thickness": 0.75,
                "value": max_val * 0.85
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        height=220,
        font_color="#ffffff"
    )
    return fig

g1, g2, g3, g4 = st.columns(4)
g1.plotly_chart(make_gauge("VOLTAGE",   voltage,  25,  "#0072ff", "#00f5ff", " V"), use_container_width=True)
g2.plotly_chart(make_gauge("CURRENT",   current,   5,  "#ff6b35", "#ffaa00", " A"), use_container_width=True)
g3.plotly_chart(make_gauge("POWER",     power,    20,  "#00ff88", "#00c6ff", " W"), use_container_width=True)
g4.plotly_chart(make_gauge("BATTERY",   battery, 100,  "#ff3232", "#00ff88", " %"), use_container_width=True)

st.markdown("---")

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
        line=dict(color="#00f5ff", width=2),
        fillcolor="rgba(0,245,255,0.08)",
        name="Power (W)"
    ))
    fig_power.update_layout(
        title=dict(text="⚡ Power Generation Over Time", font=dict(color="#00f5ff", family="Orbitron", size=13)),
        paper_bgcolor="rgba(13,31,60,0.7)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#4a7ab5",
        xaxis=dict(gridcolor="#1e3a6e", showgrid=True),
        yaxis=dict(gridcolor="#1e3a6e", showgrid=True, title="Watts"),
        height=300,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig_power, use_container_width=True)

# Vehicle Count
with r1c2:
    vehicle_cum = df["vehicle"].cumsum()
    fig_veh = go.Figure()
    fig_veh.add_trace(go.Bar(
        y=df["vehicle"],
        marker_color="#0072ff",
        marker_line_color="#00f5ff",
        marker_line_width=0.5,
        name="Vehicles"
    ))
    fig_veh.update_layout(
        title=dict(text="🚗 Vehicle Traffic Count", font=dict(color="#00f5ff", family="Orbitron", size=13)),
        paper_bgcolor="rgba(13,31,60,0.7)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#4a7ab5",
        xaxis=dict(gridcolor="#1e3a6e"),
        yaxis=dict(gridcolor="#1e3a6e", title="Vehicles"),
        height=300,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig_veh, use_container_width=True)

# Voltage & Current Over Time + V vs I scatter
r2c1, r2c2 = st.columns(2)

with r2c1:
    fig_vi = make_subplots(specs=[[{"secondary_y": True}]])
    fig_vi.add_trace(go.Scatter(
        y=df["voltage"], mode="lines",
        line=dict(color="#ff6b35", width=1.5),
        name="Voltage (V)"
    ), secondary_y=False)
    fig_vi.add_trace(go.Scatter(
        y=df["current"], mode="lines",
        line=dict(color="#00ff88", width=1.5),
        name="Current (A)"
    ), secondary_y=True)
    fig_vi.update_layout(
        title=dict(text="📈 Voltage & Current Trends", font=dict(color="#00f5ff", family="Orbitron", size=13)),
        paper_bgcolor="rgba(13,31,60,0.7)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#4a7ab5",
        xaxis=dict(gridcolor="#1e3a6e"),
        yaxis=dict(gridcolor="#1e3a6e",  title="Voltage (V)"),
        yaxis2=dict(gridcolor="#1e3a6e", title="Current (A)"),
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_vi, use_container_width=True)

with r2c2:
    fig_scatter = px.scatter(
        df, x="voltage", y="current",
        color="power",
        color_continuous_scale="blues",
        size="power",
        title="🔬 Voltage vs Current Relationship"
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(13,31,60,0.7)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#4a7ab5",
        xaxis=dict(gridcolor="#1e3a6e", title="Voltage (V)"),
        yaxis=dict(gridcolor="#1e3a6e", title="Current (A)"),
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        title_font=dict(color="#00f5ff", family="Orbitron", size=13),
        coloraxis_colorbar=dict(tickfont=dict(color="#4a7ab5"))
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
#  AI Prediction Section
# ─────────────────────────────────────────
if show_ai and len(df) >= 5:
    st.markdown('<div class="section-header">🤖 AI Energy Prediction</div>', unsafe_allow_html=True)

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
            line=dict(color="#00f5ff", width=2),
            marker=dict(size=4),
            name="Actual Power"
        ))
        fig_ai.add_trace(go.Scatter(
            x=list(range(len(df), len(df)+future_steps)),
            y=pred_power,
            mode="lines+markers",
            line=dict(color="#ff6b35", width=2, dash="dash"),
            marker=dict(size=6, symbol="diamond", color="#ff6b35"),
            name="AI Prediction"
        ))
        fig_ai.add_vrect(
            x0=len(df)-0.5, x1=len(df)+future_steps-0.5,
            fillcolor="rgba(255,107,53,0.05)",
            line_width=0,
            annotation_text="Prediction Zone",
            annotation_font_color="#ff6b35"
        )
        fig_ai.update_layout(
            title=dict(text="⚡ Power Prediction – Next 10 Readings",
                       font=dict(color="#00f5ff", family="Orbitron", size=13)),
            paper_bgcolor="rgba(13,31,60,0.7)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#4a7ab5",
            xaxis=dict(gridcolor="#1e3a6e"),
            yaxis=dict(gridcolor="#1e3a6e", title="Power (W)"),
            height=320,
            margin=dict(l=10, r=10, t=50, b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
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
            <div style='background:rgba(13,31,60,0.8);border:1px solid #1e3a6e;
                        border-radius:8px;padding:10px 14px;margin-bottom:8px;
                        display:flex;justify-content:space-between;align-items:center;'>
                <span style='font-family:Rajdhani;color:#4a7ab5;font-size:0.85rem;'>{label}</span>
                <span style='font-family:Orbitron;color:#00f5ff;font-size:0.9rem;font-weight:700;'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

# ─────────────────────────────────────────
#  Smart City Insights
# ─────────────────────────────────────────
st.markdown('<div class="section-header">🌆 Smart City Insights</div>', unsafe_allow_html=True)

total_energy_kwh = round(df["power"].sum() / 1000, 4)
co2_saved_g      = round(total_energy_kwh * 820, 2)   # 820g CO2 per kWh
led_hours        = round(total_energy_kwh * 1000 / 10, 1)  # 10W LED
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
        <div style='background:linear-gradient(135deg,#0d1f3c,#112244);
                    border:1px solid #1e3a6e;border-radius:16px;
                    padding:20px;text-align:center;
                    box-shadow:0 0 15px rgba(0,255,136,0.1);'>
            <div style='font-size:2rem;'>{icon}</div>
            <div style='font-family:Rajdhani;color:#4a7ab5;font-size:0.8rem;
                        letter-spacing:2px;text-transform:uppercase;'>{label}</div>
            <div style='font-family:Orbitron;color:#00ff88;font-size:1.5rem;
                        font-weight:700;'>{value}</div>
            <div style='font-family:Rajdhani;color:#4a7ab5;font-size:0.8rem;'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# SDG badges
st.markdown("""
<div style='text-align:center;margin:1rem 0;'>
    <span style='font-family:Rajdhani;color:#4a7ab5;letter-spacing:2px;
                 font-size:0.85rem;text-transform:uppercase;margin-right:10px;'>
        Aligned with UN SDGs:
    </span>
    <span style='background:#FCC30B;color:#000;padding:4px 10px;border-radius:6px;
                 font-weight:700;font-size:0.85rem;margin:3px;display:inline-block;'>
        SDG 7 Clean Energy
    </span>
    <span style='background:#FD6925;color:#fff;padding:4px 10px;border-radius:6px;
                 font-weight:700;font-size:0.85rem;margin:3px;display:inline-block;'>
        SDG 9 Innovation
    </span>
    <span style='background:#FD9D24;color:#fff;padding:4px 10px;border-radius:6px;
                 font-weight:700;font-size:0.85rem;margin:3px;display:inline-block;'>
        SDG 11 Sustainable Cities
    </span>
    <span style='background:#3F7E44;color:#fff;padding:4px 10px;border-radius:6px;
                 font-weight:700;font-size:0.85rem;margin:3px;display:inline-block;'>
        SDG 13 Climate Action
    </span>
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
    bat_color  = "#00ff88" if bat_level > 60 else "#ffc800" if bat_level > 30 else "#ff3232"
    bat_status = "🟢 Healthy" if bat_level > 60 else "🟡 Moderate" if bat_level > 30 else "🔴 Low"
    st.markdown(f"""
    <div style='background:rgba(13,31,60,0.8);border:1px solid {bat_color};
                border-radius:16px;padding:24px;text-align:center;'>
        <div style='font-family:Rajdhani;color:#4a7ab5;font-size:0.85rem;
                    letter-spacing:2px;text-transform:uppercase;'>Battery Level</div>
        <div style='font-family:Orbitron;color:{bat_color};font-size:3rem;
                    font-weight:900;'>{bat_level}%</div>
        <div style='font-family:Rajdhani;color:{bat_color};font-size:1rem;'>{bat_status}</div>
        <div style='background:#1e3a6e;border-radius:20px;height:12px;margin-top:14px;overflow:hidden;'>
            <div style='background:{bat_color};height:100%;width:{bat_level}%;
                        border-radius:20px;transition:width 0.5s;'></div>
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
            line=dict(color="#00ff88", width=2),
            fillcolor="rgba(0,255,136,0.07)",
            name="Battery %"
        ))
        fig_bat.update_layout(
            title=dict(text="🔋 Battery Level Over Time",
                       font=dict(color="#00f5ff", family="Orbitron", size=13)),
            paper_bgcolor="rgba(13,31,60,0.7)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#4a7ab5",
            xaxis=dict(gridcolor="#1e3a6e"),
            yaxis=dict(gridcolor="#1e3a6e", title="Battery %", range=[0, 105]),
            height=200,
            margin=dict(l=10, r=10, t=50, b=10)
        )
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
<div style='text-align:center;padding:2rem 0 1rem;
            font-family:Rajdhani;color:#1e3a6e;font-size:0.85rem;letter-spacing:2px;'>
    ROADVOLT SMART ENERGY SYSTEM  ·  HACKATHON 2026  ·  ⚡ POWERED BY IoT + AI
</div>
""", unsafe_allow_html=True)
