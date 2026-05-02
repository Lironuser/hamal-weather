#"streamlit run app.py" - To start the app.

import streamlit as st
import requests
import pandas as pd
import time
import json
from datetime import datetime
import folium
from streamlit_folium import st_folium
from deep_translator import GoogleTranslator

# ===== CONFIG =====
API_KEY = "c88dbf32015479ed56b386340beff25d"
DATA_FILE = "bases.json"
URL = "https://api.openweathermap.org/data/2.5/weather"

st.set_page_config(page_title="HAMAL SKY CONTROL", layout="wide", page_icon="🛰️")

# ===== GLOBAL STYLES =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --primary:   #00ff9c;
    --secondary: #00c8ff;
    --danger:    #ff3b3b;
    --warning:   #ffb800;
    --dark:      #020c08;
    --panel:     rgba(0, 255, 156, 0.04);
    --border:    rgba(0, 255, 156, 0.18);
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    color: #c8ffe6 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #000d06 !important;
    border-right: 1px solid var(--border) !important;
}

/* scanline overlay */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,255,156,0.015) 2px,
        rgba(0,255,156,0.015) 4px
    );
    pointer-events: none;
    z-index: 9998;
}

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: var(--primary) !important;
    text-shadow: 0 0 20px rgba(0,255,156,0.6), 0 0 40px rgba(0,255,156,0.2) !important;
    letter-spacing: 3px !important;
}

/* ── Inputs ── */
input, textarea, select {
    background: rgba(0,255,156,0.06) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--primary) !important;
    font-family: 'Share Tech Mono', monospace !important;
    caret-color: var(--primary) !important;
}
input:focus, textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 12px rgba(0,255,156,0.3) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label {
    color: var(--primary) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, rgba(0,255,156,0.12), rgba(0,255,156,0.06)) !important;
    border: 1px solid var(--primary) !important;
    color: var(--primary) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    border-radius: 3px !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
}
[data-testid="stButton"] button:hover {
    background: rgba(0,255,156,0.2) !important;
    box-shadow: 0 0 20px rgba(0,255,156,0.4), inset 0 0 15px rgba(0,255,156,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ── Alerts / Messages ── */
[data-testid="stSuccess"] {
    background: rgba(0,255,156,0.08) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 4px !important;
    color: var(--primary) !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stError"] {
    background: rgba(255,59,59,0.08) !important;
    border: 1px solid var(--danger) !important;
    color: var(--danger) !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stWarning"] {
    background: rgba(255,184,0,0.08) !important;
    border: 1px solid var(--warning) !important;
    color: var(--warning) !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Sidebar labels ── */
[data-testid="stSidebar"] * {
    font-family: 'Rajdhani', sans-serif !important;
    color: #c8ffe6 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 12px !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    color: rgba(0,255,156,0.6) !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--primary) !important;
    text-shadow: 0 0 10px rgba(0,255,156,0.5) !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
    margin: 20px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,255,156,0.06) !important;
    border: 1px solid var(--border) !important;
    color: var(--primary) !important;
}

/* ── password field ── */
[data-testid="stTextInput"][data-baseweb="input"] input[type="password"] {
    color: var(--primary) !important;
}
</style>
""", unsafe_allow_html=True)

# ===== DATA =====
def load_bases():
    try:
        return json.load(open(DATA_FILE, encoding="utf-8"))
    except:
        return []

def save_bases(b):
    json.dump(b, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False)

# ===== FUNCTIONS =====
def translate_city(city):
    try:
        return GoogleTranslator(source='auto', target='en').translate(city)
    except:
        return city

def get_weather(city):
    return requests.get(URL, params={"q": city, "appid": API_KEY, "units": "metric"}).json()

def status(temp, wind, hum):
    score = (temp > 35) * 2 + (wind > 10) * 2 + (hum > 85)
    return "🔴 מסוכן" if score >= 4 else "🟡 בינוני" if score >= 2 else "🟢 תקין"

def status_color_hex(s):
    return "#ff3b3b" if "🔴" in s else "#ffb800" if "🟡" in s else "#00ff9c"

def color(s):
    return "red" if "🔴" in s else "orange" if "🟡" in s else "green"

def wind_direction_arrow(deg):
    arrows = ['↑ N','↗ NE','→ E','↘ SE','↓ S','↙ SW','← W','↖ NW']
    return arrows[round(deg / 45) % 8]

# ===== STATE =====
if "bases" not in st.session_state:
    st.session_state.bases = load_bases()
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "admin_anim" not in st.session_state:
    st.session_state.admin_anim = False
if "loaded" not in st.session_state:
    st.session_state.loaded = False

# ================== SPLASH SCREEN ==================
if not st.session_state.loaded:
    splash = st.empty()
    splash.markdown("""
    <style>
    .splash {
        position: fixed; top:0; left:0; width:100%; height:100%;
        background: radial-gradient(ellipse at center, #001a0a 0%, #000000 100%);
        display:flex; flex-direction:column; justify-content:center; align-items:center;
        z-index:9999;
    }
    .sat { font-size:80px; animation: orbit 2.5s linear infinite; }
    .splash-title {
        color:#00ff9c; font-size:52px; font-weight:900;
        font-family:'Orbitron',monospace; letter-spacing:6px; margin-top:24px;
        text-shadow: 0 0 30px #00ff9c, 0 0 60px rgba(0,255,156,0.3);
    }
    .splash-sub {
        color:rgba(0,255,156,0.5); font-size:14px;
        font-family:'Share Tech Mono',monospace; letter-spacing:8px; margin-top:12px;
        animation: blink 1.5s step-end infinite;
    }
    .radar {
        position:absolute; width:300px; height:300px;
        border-radius:50%; border:1px solid rgba(0,255,156,0.15);
        animation: radarPulse 2s ease-out infinite;
    }
    @keyframes orbit {
        0%   { transform: rotate(0deg)   translateX(14px) rotate(0deg); }
        100% { transform: rotate(360deg) translateX(14px) rotate(-360deg); }
    }
    @keyframes blink { 50% { opacity: 0; } }
    @keyframes radarPulse {
        0%   { transform: scale(0.6); opacity: 0.8; }
        100% { transform: scale(2.4); opacity: 0; }
    }
    </style>
    <div class="splash">
        <div class="radar"></div>
        <div class="sat">🛰️</div>
        <div class="splash-title">HAMAL SKY CONTROL</div>
        <div class="splash-sub">INITIALIZING SYSTEMS...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3.2)
    splash.empty()
    st.session_state.loaded = True

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0 8px;">
        <div style="font-family:'Orbitron',monospace; font-size:13px; color:#00ff9c;
                    letter-spacing:4px; text-shadow:0 0 10px #00ff9c;">
            ⬡ HAMAL ⬡
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:10px;
                    color:rgba(0,255,156,0.4); letter-spacing:3px; margin-top:4px;">
            SKY CONTROL v2.1
        </div>
    </div>
    <hr style="border-color:rgba(0,255,156,0.15); margin:8px 0 16px;">
    """, unsafe_allow_html=True)

    # Clock
    now = datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y")
    st.markdown(f"""
    <div style="text-align:center; font-family:'Share Tech Mono',monospace;
                font-size:11px; color:rgba(0,255,156,0.55); letter-spacing:2px;
                margin-bottom:16px;">
        🕐 {now}
    </div>
    """, unsafe_allow_html=True)

    # Base counter
    total = len(st.session_state.bases)
    danger_count = sum(1 for b in st.session_state.bases if "🔴" in b.get("status",""))
    warn_count   = sum(1 for b in st.session_state.bases if "🟡" in b.get("status",""))
    ok_count     = sum(1 for b in st.session_state.bases if "🟢" in b.get("status",""))

    st.markdown(f"""
    <div style="background:rgba(0,255,156,0.04); border:1px solid rgba(0,255,156,0.15);
                border-radius:6px; padding:12px; margin-bottom:16px; direction:rtl;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:10px;
                    color:rgba(0,255,156,0.45); letter-spacing:2px; margin-bottom:8px;">
            STATUS OVERVIEW
        </div>
        <div style="display:flex; justify-content:space-between; font-family:'Orbitron',monospace; font-size:13px;">
            <span style="color:#ff3b3b;">⬤ {danger_count}</span>
            <span style="color:#ffb800;">⬤ {warn_count}</span>
            <span style="color:#00ff9c;">⬤ {ok_count}</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-family:'Share Tech Mono',monospace;
                    font-size:9px; color:rgba(0,255,156,0.4); margin-top:4px;">
            <span>DANGER</span><span>CAUTION</span><span>CLEAR</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(0,255,156,0.1);'>", unsafe_allow_html=True)

    # ── Admin toggle ──
    if not st.session_state.admin_mode:
        if st.button("🔐 כניסה למצב אחמש", use_container_width=True):
            st.session_state._pending_admin = True
            st.rerun()

        if st.session_state.get("_pending_admin"):
            pwd = st.text_input("🔑 סיסמה", type="password", key="pwd_input")
            if pwd:
                if pwd == "1234":
                    st.session_state.admin_mode = True
                    st.session_state.admin_anim = True
                    st.session_state._pending_admin = False
                    st.rerun()
                else:
                    st.error("❌ סיסמה שגויה")
    else:
        st.markdown("""
        <div style="background:rgba(0,255,156,0.08); border:1px solid rgba(0,255,156,0.35);
                    border-radius:6px; padding:10px; text-align:center; margin-bottom:10px;">
            <span style="font-family:'Share Tech Mono',monospace; font-size:11px;
                         color:#00ff9c; letter-spacing:2px;">
                🔓 ADMIN ACTIVE
            </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔒 יציאה ממצב אחמש", use_container_width=True):
            st.session_state.admin_mode = False
            st.session_state.admin_anim = False
            st.session_state._pending_admin = False
            st.rerun()

is_admin = st.session_state.admin_mode

# ================== ADMIN ACCESS ANIMATION ==================
if st.session_state.get("admin_anim"):
    overlay = st.empty()
    overlay.markdown("""
    <style>
    .overlay {
        position:fixed; top:0; left:0; width:100%; height:100%;
        background:rgba(0,0,0,0.96);
        display:flex; justify-content:center; align-items:center; flex-direction:column;
        z-index:9999;
    }
    .lock { font-size:72px; animation: pulse 0.8s ease-in-out 3; }
    .access-text {
        color:#00ff9c; font-size:44px; margin-top:18px;
        font-family:'Orbitron',monospace; letter-spacing:4px;
        text-shadow:0 0 20px #00ff9c, 0 0 40px rgba(0,255,156,0.4);
    }
    .access-sub {
        color:rgba(0,255,156,0.5); font-size:13px; margin-top:10px;
        font-family:'Share Tech Mono',monospace; letter-spacing:6px;
    }
    @keyframes pulse {
        0%,100% { transform:scale(1);   filter:drop-shadow(0 0 0px #00ff9c); }
        50%      { transform:scale(1.3); filter:drop-shadow(0 0 20px #00ff9c); }
    }
    </style>
    <div class="overlay">
        <div class="lock">🔓</div>
        <div class="access-text">גישה אושרה</div>
        <div class="access-sub">ADMIN MODE ENABLED</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.5)
    overlay.empty()
    st.session_state.admin_anim = False

# ================== HEADER ==================
st.markdown("""
<div style="display:flex; align-items:center; gap:16px; margin-bottom:24px; padding-bottom:16px;
            border-bottom:1px solid rgba(0,255,156,0.15);">
    <div style="font-size:42px; filter:drop-shadow(0 0 12px #00ff9c);">🛰️</div>
    <div>
        <h1 style="margin:0; font-family:'Orbitron',monospace; font-size:28px; color:#00ff9c;
                   text-shadow:0 0 20px rgba(0,255,156,0.6), 0 0 40px rgba(0,255,156,0.2);
                   letter-spacing:5px;">
            HAMAL SKY CONTROL
        </h1>
        <div style="font-family:'Share Tech Mono',monospace; font-size:11px;
                    color:rgba(0,255,156,0.4); letter-spacing:4px; margin-top:4px;">
            מערכת ניטור מזג אוויר מבצעי · OPERATIONAL WEATHER MONITORING
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================== SEARCH ==================
st.markdown("""
<div style="font-family:'Share Tech Mono',monospace; font-size:11px;
            color:rgba(0,255,156,0.5); letter-spacing:3px; margin-bottom:6px;">
    ⌕ SEARCH BASE / CITY
</div>
""", unsafe_allow_html=True)

city = st.text_input("חיפוש (עברית/אנגלית)", label_visibility="collapsed",
                     placeholder="הזן שם בסיס או עיר...")

if city:
    found_base = next(
        (b for b in st.session_state.bases if city.strip().lower() in b["name"].lower()),
        None
    )

    if found_base:
        r = requests.get(URL, params={
            "lat": found_base["lat"], "lon": found_base["lon"],
            "appid": API_KEY, "units": "metric"
        }).json()

        if "main" in r:
            temp  = r["main"]["temp"]
            hum   = r["main"]["humidity"]
            wind  = r["wind"]["speed"]
            wdir  = r["wind"].get("deg", 0)
            desc  = r["weather"][0].get("description", "")
            s     = status(temp, wind, hum)
            scolor = status_color_hex(s)

            st.markdown(f"""
            <div style="background:rgba(0,255,156,0.04); border:1px solid {scolor}44;
                        border-left:3px solid {scolor}; border-radius:6px; padding:16px;
                        margin-bottom:20px; direction:rtl;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div>
                        <div style="font-family:'Orbitron',monospace; font-size:16px;
                                    color:{scolor}; letter-spacing:2px;">
                            📍 {found_base['name']}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:10px;
                                    color:rgba(0,255,156,0.4); margin-top:4px;">
                            {found_base['lat']:.4f}°N · {found_base['lon']:.4f}°E
                        </div>
                    </div>
                    <div style="font-family:'Orbitron',monospace; font-size:14px;
                                color:{scolor}; text-align:center;
                                text-shadow:0 0 10px {scolor};">
                        {s}
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:10px;">
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,255,156,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">🌡️</div>
                        <div style="font-family:'Orbitron',monospace; font-size:16px; color:#00ff9c;">{temp}°</div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(0,255,156,0.4); letter-spacing:1px;">TEMP °C</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,255,156,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">💧</div>
                        <div style="font-family:'Orbitron',monospace; font-size:16px; color:#00c8ff;">{hum}%</div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(0,200,255,0.4); letter-spacing:1px;">HUMIDITY</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,255,156,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">🌬️</div>
                        <div style="font-family:'Orbitron',monospace; font-size:16px; color:#ffb800;">{wind}</div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(255,184,0,0.4); letter-spacing:1px;">WIND m/s</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,255,156,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">🧭</div>
                        <div style="font-family:'Orbitron',monospace; font-size:14px; color:#c8ffe6;">
                            {wind_direction_arrow(wdir)}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(200,255,230,0.4); letter-spacing:1px;">DIRECTION</div>
                    </div>
                </div>
                <div style="margin-top:10px; font-family:'Share Tech Mono',monospace; font-size:11px;
                            color:rgba(0,255,156,0.4); text-align:center;">
                    ☁ {desc.upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("שגיאה בקבלת נתוני מזג אוויר")

    else:
        city_en = translate_city(city)
        data = get_weather(city_en)

        if "main" in data:
            temp  = data["main"]["temp"]
            hum   = data["main"]["humidity"]
            wind  = data["wind"]["speed"]
            wdir  = data["wind"].get("deg", 0)
            desc  = data["weather"][0].get("description", "")
            s     = status(temp, wind, hum)
            scolor = status_color_hex(s)

            st.markdown(f"""
            <div style="background:rgba(0,200,255,0.04); border:1px solid rgba(0,200,255,0.25);
                        border-left:3px solid #00c8ff; border-radius:6px; padding:16px;
                        margin-bottom:20px; direction:rtl;">
                <div style="font-family:'Orbitron',monospace; font-size:14px;
                            color:#00c8ff; letter-spacing:2px; margin-bottom:12px;">
                    🌍 {city_en.upper()}  <span style="font-size:11px; color:{scolor};">{s}</span>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:10px;">
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,200,255,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">🌡️</div>
                        <div style="font-family:'Orbitron',monospace; font-size:16px; color:#00ff9c;">{temp}°</div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(0,255,156,0.4);">TEMP °C</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,200,255,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">💧</div>
                        <div style="font-family:'Orbitron',monospace; font-size:16px; color:#00c8ff;">{hum}%</div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(0,200,255,0.4);">HUMIDITY</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,200,255,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">🌬️</div>
                        <div style="font-family:'Orbitron',monospace; font-size:16px; color:#ffb800;">{wind}</div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(255,184,0,0.4);">WIND m/s</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,200,255,0.1);
                                border-radius:4px; padding:10px; text-align:center;">
                        <div style="font-size:22px;">🧭</div>
                        <div style="font-family:'Orbitron',monospace; font-size:14px; color:#c8ffe6;">
                            {wind_direction_arrow(wdir)}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                                    color:rgba(200,255,230,0.4);">DIRECTION</div>
                    </div>
                </div>
                <div style="margin-top:10px; font-family:'Share Tech Mono',monospace; font-size:11px;
                            color:rgba(0,200,255,0.4); text-align:center;">
                    ☁ {desc.upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ לא נמצא — BASE OR CITY UNKNOWN")

st.markdown("<hr style='border-color:rgba(0,255,156,0.1); margin:10px 0 20px;'>", unsafe_allow_html=True)

# ================== MAP ==================
st.markdown("""
<div style="font-family:'Share Tech Mono',monospace; font-size:11px;
            color:rgba(0,255,156,0.5); letter-spacing:3px; margin-bottom:8px;">
    ◈ TACTICAL MAP — CLICK TO SELECT COORDINATES
</div>
""", unsafe_allow_html=True)

m = folium.Map(
    location=[31.5, 34.8],
    zoom_start=7,
    tiles="CartoDB dark_matter"
)

# Grid overlay style
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Esri Dark",
    overlay=False,
    control=True,
).add_to(m)

for b in st.session_state.bases:
    sc = status_color_hex(b.get("status", "🟢"))

    # Pulse ring
    folium.CircleMarker(
        location=[b["lat"], b["lon"]],
        radius=18,
        color=sc,
        fill=False,
        weight=1,
        opacity=0.35,
    ).add_to(m)

    # Main dot
    folium.CircleMarker(
        location=[b["lat"], b["lon"]],
        radius=9,
        color=sc,
        fill=True,
        fill_color=sc,
        fill_opacity=0.85,
        weight=2,
        tooltip=folium.Tooltip(
            f"""<div style='font-family:monospace; font-size:13px; background:#000d06;
                           color:{sc}; padding:8px; border:1px solid {sc};
                           border-radius:4px;'>
                <b>{b['name']}</b><br>
                🌡 {b.get('temp','—')}° &nbsp; 💧{b.get('hum','—')}% &nbsp; 🌬{b.get('wind','—')} m/s<br>
                {b.get('status','—')}
                </div>""",
            sticky=True
        )
    ).add_to(m)

    # Label
    folium.Marker(
        [b["lat"], b["lon"]],
        icon=folium.DivIcon(html=f"""
        <div style="
            color:{sc};
            font-family:'Share Tech Mono',monospace;
            font-weight:bold;
            font-size:11px;
            white-space:nowrap;
            margin-top:-28px;
            text-shadow:0 0 6px {sc}, 0 0 12px {sc}77;
            letter-spacing:1px;
        ">
        {b['name']}
        </div>
        """)
    ).add_to(m)

map_data = st_folium(m, width="100%", height=520)

st.markdown("<hr style='border-color:rgba(0,255,156,0.1); margin:20px 0;'>", unsafe_allow_html=True)

# ================== BASE TABLE ==================
if st.session_state.bases:
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; font-size:11px;
                color:rgba(0,255,156,0.5); letter-spacing:3px; margin-bottom:12px;">
        ◉ ACTIVE BASES — WEATHER STATUS
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(min(len(st.session_state.bases), 3))
    for i, b in enumerate(st.session_state.bases):
        sc = status_color_hex(b.get("status", "🟢"))
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.4); border:1px solid {sc}44;
                        border-top:2px solid {sc}; border-radius:6px; padding:14px;
                        margin-bottom:12px; direction:rtl;">
                <div style="font-family:'Orbitron',monospace; font-size:13px;
                            color:{sc}; letter-spacing:2px; margin-bottom:8px;">
                    {b['name']}
                </div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:11px;
                            line-height:1.9; color:rgba(200,255,230,0.8);">
                    🌡 {b.get('temp','—')}°C &nbsp;&nbsp;
                    💧 {b.get('hum','—')}% &nbsp;&nbsp;
                    🌬 {b.get('wind','—')} m/s
                </div>
                <div style="margin-top:8px; font-family:'Orbitron',monospace;
                            font-size:11px; color:{sc}; text-shadow:0 0 8px {sc};">
                    {b.get('status','—')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================== ADMIN PANEL ==================
if is_admin:
    st.markdown("""
    <div style="background:rgba(0,255,156,0.04); border:1px solid rgba(0,255,156,0.25);
                border-radius:8px; padding:20px; margin-top:20px;">
        <div style="font-family:'Orbitron',monospace; font-size:14px; color:#00ff9c;
                    letter-spacing:3px; margin-bottom:16px; text-align:center;">
            ⬡ ADMIN CONTROL PANEL ⬡
        </div>
    """, unsafe_allow_html=True)

    tab_add, tab_del, tab_edit = st.tabs(["➕ הוסף בסיס", "❌ מחק בסיס", "✏️ ערוך בסיס"])

    with tab_add:
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]

            st.markdown(f"""
            <div style="font-family:'Share Tech Mono',monospace; font-size:11px;
                        color:rgba(0,255,156,0.6); margin-bottom:10px;">
                📍 נבחר: {lat:.5f}°N · {lon:.5f}°E
            </div>
            """, unsafe_allow_html=True)

            name = st.text_input("שם הבסיס", placeholder="הזן שם...", key="add_name")

            if st.button("➕ הוסף בסיס", use_container_width=True):
                if name:
                    w = requests.get(URL, params={
                        "lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"
                    }).json()

                    if "main" in w:
                        t  = w["main"]["temp"]
                        h  = w["main"]["humidity"]
                        wd = w["wind"]["speed"]
                        s  = status(t, wd, h)

                        st.session_state.bases.append({
                            "name": name, "lat": lat, "lon": lon,
                            "temp": t, "hum": h, "wind": wd,
                            "status": s, "color": color(s)
                        })
                        save_bases(st.session_state.bases)
                        st.success(f"✅ בסיס '{name}' נוסף בהצלחה")
                        st.rerun()
                    else:
                        st.error("שגיאה בקבלת נתונים למיקום")
                else:
                    st.warning("יש להזין שם לבסיס")
        else:
            st.info("🗺 לחץ על המפה כדי לבחור מיקום לבסיס חדש")

    with tab_del:
        if st.session_state.bases:
            names = [b["name"] for b in st.session_state.bases]
            sel_del = st.selectbox("בחר בסיס למחיקה", names, key="del_select")
            if st.button("❌ מחק בסיס", use_container_width=True):
                st.session_state.bases = [b for b in st.session_state.bases if b["name"] != sel_del]
                save_bases(st.session_state.bases)
                st.success(f"🗑 בסיס '{sel_del}' נמחק")
                st.rerun()
        else:
            st.info("אין בסיסים קיימים")

    with tab_edit:
        if st.session_state.bases:
            sel_edit = st.selectbox("בחר בסיס לעריכה", [b["name"] for b in st.session_state.bases], key="edit_select")
            base     = next(b for b in st.session_state.bases if b["name"] == sel_edit)
            new_name = st.text_input("שם חדש", value=base["name"], key="edit_name")

            if st.button("💾 שמור שינויים", use_container_width=True):
                base["name"] = new_name
                save_bases(st.session_state.bases)
                st.success("✅ השינויים נשמרו")
                st.rerun()
        else:
            st.info("אין בסיסים לעריכה")

    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div style="text-align:center; padding:30px 0 10px; font-family:'Share Tech Mono',monospace;
            font-size:10px; color:rgba(0,255,156,0.2); letter-spacing:3px;">
    HAMAL SKY CONTROL · CLASSIFIED · ALL RIGHTS RESERVED
</div>
""", unsafe_allow_html=True)