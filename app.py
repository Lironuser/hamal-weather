# "streamlit run app.py" - To start the app.

import streamlit as st
import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from deep_translator import GoogleTranslator
from collections import defaultdict

# ===== CONFIG =====
API_KEY = "c88dbf32015479ed56b386340beff25d"
DATA_FILE = "bases.json"
URL       = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

st.set_page_config(page_title="Plugot hamal sky control", layout="wide", page_icon="🛰️")

# ===== GLOBAL STYLES =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Heebo:wght@300;400;500;600;700;900&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --primary:   #00ff9c;
    --secondary: #00c8ff;
    --danger:    #ff3b3b;
    --warning:   #ffb800;
    --dark:      #020c08;
    --panel:     rgba(0, 255, 156, 0.04);
    --border:    rgba(0, 255, 156, 0.18);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    color: #c8ffe6 !important;
    font-family: 'Heebo', sans-serif !important;
    direction: rtl;
}

[data-testid="stSidebar"] {
    background: #000d06 !important;
    border-right: none !important;
    border-left: 1px solid var(--border) !important;
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
        rgba(0,255,156,0.012) 2px,
        rgba(0,255,156,0.012) 4px
    );
    pointer-events: none;
    z-index: 9998;
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: var(--primary) !important;
    text-shadow: 0 0 20px rgba(0,255,156,0.6), 0 0 40px rgba(0,255,156,0.2) !important;
    letter-spacing: 2px !important;
}

input, textarea, select {
    background: rgba(0,255,156,0.06) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--primary) !important;
    font-family: 'Heebo', sans-serif !important;
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

[data-testid="stButton"] button {
    background: linear-gradient(135deg, rgba(0,255,156,0.12), rgba(0,255,156,0.04)) !important;
    border: 1px solid var(--primary) !important;
    color: var(--primary) !important;
    font-family: 'Heebo', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    border-radius: 4px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] button:hover {
    background: rgba(0,255,156,0.2) !important;
    box-shadow: 0 0 20px rgba(0,255,156,0.4), inset 0 0 15px rgba(0,255,156,0.1) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stSuccess"] {
    background: rgba(0,255,156,0.08) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 4px !important;
    color: var(--primary) !important;
    font-family: 'Heebo', sans-serif !important;
}
[data-testid="stError"] {
    background: rgba(255,59,59,0.08) !important;
    border: 1px solid var(--danger) !important;
    color: var(--danger) !important;
    font-family: 'Heebo', sans-serif !important;
}
[data-testid="stWarning"] {
    background: rgba(255,184,0,0.08) !important;
    border: 1px solid var(--warning) !important;
    color: var(--warning) !important;
    font-family: 'Heebo', sans-serif !important;
}

[data-testid="stSidebar"] * {
    font-family: 'Heebo', sans-serif !important;
    color: #c8ffe6 !important;
}

[data-testid="stMetric"] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 12px !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Heebo', sans-serif !important;
    font-size: 12px !important;
    color: rgba(0,255,156,0.6) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--primary) !important;
    text-shadow: 0 0 10px rgba(0,255,156,0.5) !important;
}

hr { border-color: var(--border) !important; margin: 20px 0 !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

[data-testid="stSelectbox"] > div > div {
    background: rgba(0,255,156,0.06) !important;
    border: 1px solid var(--border) !important;
    color: var(--primary) !important;
}

/* tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(0,255,156,0.04) !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: rgba(0,255,156,0.5) !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* info */
[data-testid="stInfo"] {
    background: rgba(0,200,255,0.06) !important;
    border: 1px solid rgba(0,200,255,0.25) !important;
    color: #00c8ff !important;
    font-family: 'Heebo', sans-serif !important;
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

def get_weather_by_coords(lat, lon):
    return requests.get(URL, params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}).json()

def get_forecast_by_coords(lat, lon):
    return requests.get(FORECAST_URL, params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric", "cnt": 40}).json()

def get_forecast_by_city(city):
    return requests.get(FORECAST_URL, params={"q": city, "appid": API_KEY, "units": "metric", "cnt": 40}).json()

def status(temp, wind, hum):
    score = (temp > 35) * 2 + (wind > 10) * 2 + (hum > 85)
    return "🔴 מסוכן" if score >= 4 else "🟡 בינוני" if score >= 2 else "🟢 תקין"

def status_color_hex(s):
    return "#ff3b3b" if "🔴" in s else "#ffb800" if "🟡" in s else "#00ff9c"

def color(s):
    return "red" if "🔴" in s else "orange" if "🟡" in s else "green"

def wind_direction_arrow(deg):
    arrows = ['↑ צ','↗ צמ','→ מ','↘ דמ','↓ ד','↙ דמע','← מע','↖ צמע']
    return arrows[round(deg / 45) % 8]

DAYS_HE = ['שני','שלישי','רביעי','חמישי','שישי','שבת','ראשון']
MONTHS_HE = ['ינו','פבר','מרץ','אפר','מאי','יוני','יולי','אוג','ספט','אוק','נוב','דצמ']

def format_date_he(dt_str):
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    day_name = DAYS_HE[dt.weekday()]
    return f"{day_name} {dt.day} {MONTHS_HE[dt.month-1]}"

def weather_icon(description):
    desc = description.lower()
    if "thunderstorm" in desc: return "⛈️"
    if "drizzle" in desc: return "🌦️"
    if "rain" in desc: return "🌧️"
    if "snow" in desc: return "❄️"
    if "fog" in desc or "mist" in desc or "haze" in desc: return "🌫️"
    if "cloud" in desc: return "☁️"
    if "clear" in desc: return "☀️"
    return "🌤️"

def build_daily_forecast(forecast_data):
    """Group 3-hourly forecast into daily summaries."""
    if "list" not in forecast_data:
        return []
    daily = defaultdict(list)
    for item in forecast_data["list"]:
        date = item["dt_txt"][:10]
        daily[date].append(item)
    result = []
    today = datetime.now().date()
    for date_str, items in sorted(daily.items()):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj < today:
            continue
        temps = [i["main"]["temp"] for i in items]
        winds = [i["wind"]["speed"] for i in items]
        hums  = [i["main"]["humidity"] for i in items]
        descs = [i["weather"][0]["description"] for i in items]
        # pick noon or midday slot description
        noon_items = [i for i in items if "12:00" in i["dt_txt"] or "15:00" in i["dt_txt"]]
        main_desc = noon_items[0]["weather"][0]["description"] if noon_items else descs[len(descs)//2]
        result.append({
            "date": date_str,
            "label": format_date_he(items[len(items)//2]["dt_txt"]),
            "temp_max": round(max(temps)),
            "temp_min": round(min(temps)),
            "wind_avg": round(sum(winds)/len(winds), 1),
            "hum_avg":  round(sum(hums)/len(hums)),
            "desc": main_desc,
            "icon": weather_icon(main_desc),
            "status": status(max(temps), max(winds), max(hums)),
        })
    return result[:7]

def render_current_weather(name, temp, hum, wind, wdir, desc, s, is_base=True, lat=None, lon=None):
    scolor = status_color_hex(s)
    border_color = scolor if is_base else "#00c8ff"
    icon = weather_icon(desc)
    coord_line = f"{lat:.4f}°N · {lon:.4f}°E" if lat and lon else ""
    return f"""
    <div style="background:rgba(0,0,0,0.45); border:1px solid {border_color}33;
                border-top:3px solid {border_color}; border-radius:8px; padding:20px;
                margin-bottom:16px; direction:rtl;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
            <div>
                <div style="font-family:'Orbitron',monospace; font-size:18px;
                            color:{border_color}; letter-spacing:2px;">
                    📍 {name}
                </div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(0,255,156,0.4); margin-top:4px;">
                    {coord_line}
                </div>
            </div>
            <div style="text-align:left;">
                <div style="font-size:36px; line-height:1;">{icon}</div>
                <div style="font-family:'Heebo',sans-serif; font-size:13px;
                            color:{scolor}; font-weight:700; margin-top:4px;
                            text-shadow:0 0 10px {scolor};">
                    {s}
                </div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:10px;">
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(0,255,156,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">🌡️</div>
                <div style="font-family:'Orbitron',monospace; font-size:20px; color:#00ff9c; font-weight:700;">{temp}°</div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(0,255,156,0.5);">טמפרטורה °C</div>
            </div>
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(0,200,255,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">💧</div>
                <div style="font-family:'Orbitron',monospace; font-size:20px; color:#00c8ff; font-weight:700;">{hum}%</div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(0,200,255,0.5);">לחות</div>
            </div>
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(255,184,0,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">🌬️</div>
                <div style="font-family:'Orbitron',monospace; font-size:20px; color:#ffb800; font-weight:700;">{wind}</div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(255,184,0,0.5);">רוח מ/ש</div>
            </div>
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(200,255,230,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">🧭</div>
                <div style="font-family:'Orbitron',monospace; font-size:16px; color:#c8ffe6; font-weight:700;">
                    {wind_direction_arrow(wdir)}
                </div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(200,255,230,0.5);">כיוון רוח</div>
            </div>
        </div>
        <div style="margin-top:12px; font-family:'Heebo',sans-serif; font-size:13px;
                    color:rgba(0,255,156,0.5); text-align:center; letter-spacing:1px;">
            {icon} {desc.upper()}
        </div>
    </div>
    """

def render_forecast(daily_list):
    if not daily_list:
        return ""
    cards = ""
    for d in daily_list:
        sc = status_color_hex(d["status"])
        cards += f"""
        <div style="background:rgba(0,0,0,0.4); border:1px solid {sc}33;
                    border-top:2px solid {sc}; border-radius:6px; padding:12px;
                    text-align:center; min-width:90px; flex:1;">
            <div style="font-family:'Heebo',sans-serif; font-size:12px; font-weight:700;
                        color:rgba(0,255,156,0.7); margin-bottom:6px; white-space:nowrap;">{d['label']}</div>
            <div style="font-size:28px; margin:6px 0;">{d['icon']}</div>
            <div style="font-family:'Orbitron',monospace; font-size:15px; color:#00ff9c; font-weight:700;">
                {d['temp_max']}° <span style="font-size:11px; color:rgba(0,255,156,0.4);">{d['temp_min']}°</span>
            </div>
            <div style="font-family:'Heebo',sans-serif; font-size:11px; color:rgba(0,200,255,0.6); margin-top:4px;">
                💧{d['hum_avg']}%
            </div>
            <div style="font-family:'Heebo',sans-serif; font-size:11px; color:rgba(255,184,0,0.6);">
                🌬{d['wind_avg']}מ"ש
            </div>
            <div style="font-size:10px; color:{sc}; margin-top:6px; font-weight:700;">{d['status']}</div>
        </div>
        """
    return f"""
    <div style="margin-top:16px; direction:rtl;">
        <div style="font-family:'Heebo',sans-serif; font-size:13px; font-weight:700;
                    color:rgba(0,255,156,0.6); letter-spacing:2px; margin-bottom:10px;
                    border-right:3px solid var(--primary); padding-right:10px;">
            📅 תחזית שבועית
        </div>
        <div style="display:flex; gap:8px; overflow-x:auto; padding-bottom:6px;">
            {cards}
        </div>
    </div>
    """

# ===== STATE =====
if "bases"      not in st.session_state: st.session_state.bases      = load_bases()
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "admin_anim" not in st.session_state: st.session_state.admin_anim = False
if "loaded"     not in st.session_state: st.session_state.loaded     = False
if "map_weather" not in st.session_state: st.session_state.map_weather = None

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
        color:#00ff9c; font-size:48px; font-weight:900;
        font-family:'Orbitron',monospace; letter-spacing:6px; margin-top:24px;
        text-shadow: 0 0 30px #00ff9c, 0 0 60px rgba(0,255,156,0.3);
    }
    .splash-he {
        color:rgba(0,255,156,0.7); font-size:22px; font-family:'Heebo',sans-serif;
        font-weight:700; letter-spacing:3px; margin-top:10px;
    }
    .splash-sub {
        color:rgba(0,255,156,0.4); font-size:13px;
        font-family:'Heebo',sans-serif; letter-spacing:4px; margin-top:8px;
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
        <div class="splash-he">מערכת ניטור מזג אוויר מבצעי</div>
        <div class="splash-sub">מאתחל מערכות...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3.2)
    splash.empty()
    st.session_state.loaded = True

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 12px;">
        <div style="font-family:'Orbitron',monospace; font-size:13px; color:#00ff9c;
                    letter-spacing:4px; text-shadow:0 0 10px #00ff9c;">
            ⬡ המל ⬡
        </div>
        <div style="font-family:'Heebo',sans-serif; font-size:11px;
                    color:rgba(0,255,156,0.4); letter-spacing:2px; margin-top:4px;">
            מערכת שמי שליטה · v2.2
        </div>
    </div>
    <hr style="border-color:rgba(0,255,156,0.15); margin:8px 0 16px;">
    """, unsafe_allow_html=True)

    now = datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y")
    st.markdown(f"""
    <div style="text-align:center; font-family:'Heebo',sans-serif;
                font-size:12px; color:rgba(0,255,156,0.55); letter-spacing:1px;
                margin-bottom:16px;">
        🕐 {now}
    </div>
    """, unsafe_allow_html=True)

    total        = len(st.session_state.bases)
    danger_count = sum(1 for b in st.session_state.bases if "🔴" in b.get("status",""))
    warn_count   = sum(1 for b in st.session_state.bases if "🟡" in b.get("status",""))
    ok_count     = sum(1 for b in st.session_state.bases if "🟢" in b.get("status",""))

    st.markdown(f"""
    <div style="background:rgba(0,255,156,0.04); border:1px solid rgba(0,255,156,0.15);
                border-radius:8px; padding:14px; margin-bottom:16px; direction:rtl;">
        <div style="font-family:'Heebo',sans-serif; font-size:13px; font-weight:700;
                    color:rgba(0,255,156,0.6); letter-spacing:1px; margin-bottom:10px;">
            סטטוס כללי
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#ff3b3b;">{danger_count}</div>
                <div style="font-size:10px; color:rgba(255,59,59,0.7); font-family:'Heebo',sans-serif;">מסוכן</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#ffb800;">{warn_count}</div>
                <div style="font-size:10px; color:rgba(255,184,0,0.7); font-family:'Heebo',sans-serif;">בינוני</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#00ff9c;">{ok_count}</div>
                <div style="font-size:10px; color:rgba(0,255,156,0.7); font-family:'Heebo',sans-serif;">תקין</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#c8ffe6;">{total}</div>
                <div style="font-size:10px; color:rgba(200,255,230,0.5); font-family:'Heebo',sans-serif;">סה"כ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(0,255,156,0.1);'>", unsafe_allow_html=True)

    # ── Admin toggle ──
    if not st.session_state.admin_mode:
        if st.button("🔐 כניסה למצב אדמין", use_container_width=True):
            st.session_state._pending_admin = True
            st.rerun()

        if st.session_state.get("_pending_admin"):
            pwd = st.text_input("🔑 סיסמה", type="password", key="pwd_input")
            if pwd:
                if pwd == "PlugotHamal2026!":
                    st.session_state.admin_mode = True
                    st.session_state.admin_anim = True
                    st.session_state._pending_admin = False
                    st.rerun()
                else:
                    st.error("❌ סיסמה שגויה")
    else:
        st.markdown("""
        <div style="background:rgba(0,255,156,0.08); border:1px solid rgba(0,255,156,0.35);
                    border-radius:6px; padding:12px; text-align:center; margin-bottom:10px;">
            <span style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
                         color:#00ff9c; letter-spacing:1px;">
                🔓 מצב אדמין פעיל
            </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔒 יציאה ממצב אדמין", use_container_width=True):
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
        color:#00ff9c; font-size:40px; margin-top:18px;
        font-family:'Heebo',sans-serif; font-weight:900; letter-spacing:3px;
        text-shadow:0 0 20px #00ff9c, 0 0 40px rgba(0,255,156,0.4);
    }
    .access-sub {
        color:rgba(0,255,156,0.5); font-size:14px; margin-top:8px;
        font-family:'Heebo',sans-serif; letter-spacing:2px;
    }
    @keyframes pulse {
        0%,100% { transform:scale(1);   filter:drop-shadow(0 0 0px #00ff9c); }
        50%      { transform:scale(1.3); filter:drop-shadow(0 0 20px #00ff9c); }
    }
    </style>
    <div class="overlay">
        <div class="lock">🔓</div>
        <div class="access-text">גישה אושרה</div>
        <div class="access-sub">מצב מנהל הופעל בהצלחה</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.5)
    overlay.empty()
    st.session_state.admin_anim = False

# ================== HEADER ==================
st.markdown("""
<div style="display:flex; align-items:center; gap:16px; margin-bottom:28px; padding-bottom:18px;
            border-bottom:1px solid rgba(0,255,156,0.15); direction:rtl;">
    <div style="font-size:44px; filter:drop-shadow(0 0 12px #00ff9c);">🛰️</div>
    <div>
        <h1 style="margin:0; font-family:'Orbitron',monospace; font-size:26px; color:#00ff9c;
                   text-shadow:0 0 20px rgba(0,255,156,0.6), 0 0 40px rgba(0,255,156,0.2);
                   letter-spacing:4px;">
            HAMAL SKY CONTROL
        </h1>
        <div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:500;
                    color:rgba(0,255,156,0.5); letter-spacing:1px; margin-top:4px;">
            מערכת ניטור מזג אוויר מבצעי · ניטור בזמן אמת
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================== SEARCH ==================
st.markdown("""
<div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
            color:rgba(0,255,156,0.6); letter-spacing:1px; margin-bottom:6px;
            border-right:3px solid #00ff9c; padding-right:10px;">
    🔍 חיפוש בסיס / עיר
</div>
""", unsafe_allow_html=True)

city = st.text_input("חיפוש", label_visibility="collapsed",
                     placeholder="הזן שם בסיס או עיר (עברית / אנגלית)...")

if city:
    found_base = next(
        (b for b in st.session_state.bases if city.strip().lower() in b["name"].lower()),
        None
    )

    if found_base:
        r = get_weather_by_coords(found_base["lat"], found_base["lon"])
        if "main" in r:
            temp  = r["main"]["temp"]
            hum   = r["main"]["humidity"]
            wind  = r["wind"]["speed"]
            wdir  = r["wind"].get("deg", 0)
            desc  = r["weather"][0].get("description", "")
            s     = status(temp, wind, hum)
            st.markdown(render_current_weather(
                found_base["name"], temp, hum, wind, wdir, desc, s,
                is_base=True, lat=found_base["lat"], lon=found_base["lon"]
            ), unsafe_allow_html=True)
            # Forecast
            fc = get_forecast_by_coords(found_base["lat"], found_base["lon"])
            daily = build_daily_forecast(fc)
            st.markdown(render_forecast(daily), unsafe_allow_html=True)
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
            lat   = data["coord"]["lat"]
            lon   = data["coord"]["lon"]
            st.markdown(render_current_weather(
                city_en.upper(), temp, hum, wind, wdir, desc, s,
                is_base=False, lat=lat, lon=lon
            ), unsafe_allow_html=True)
            # Forecast
            fc = get_forecast_by_city(city_en)
            daily = build_daily_forecast(fc)
            st.markdown(render_forecast(daily), unsafe_allow_html=True)
        else:
            st.error("❌ לא נמצא — בסיס או עיר לא ידועים")

st.markdown("<hr style='border-color:rgba(0,255,156,0.1); margin:16px 0 20px;'>", unsafe_allow_html=True)

# ================== MAP ==================
st.markdown("""
<div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
            color:rgba(0,255,156,0.6); letter-spacing:1px; margin-bottom:8px;
            border-right:3px solid #00ff9c; padding-right:10px;">
    🗺️ מפה טקטית — לחץ לבחירת מיקום
</div>
""", unsafe_allow_html=True)

m = folium.Map(location=[31.5, 34.8], zoom_start=7, tiles="CartoDB dark_matter")

for b in st.session_state.bases:
    sc = status_color_hex(b.get("status", "🟢"))
    folium.CircleMarker(
        location=[b["lat"], b["lon"]], radius=18,
        color=sc, fill=False, weight=1, opacity=0.35,
    ).add_to(m)
    folium.CircleMarker(
        location=[b["lat"], b["lon"]], radius=9,
        color=sc, fill=True, fill_color=sc, fill_opacity=0.85, weight=2,
        tooltip=folium.Tooltip(
            f"""<div style='font-family:monospace; font-size:13px; background:#000d06;
                           color:{sc}; padding:8px; border:1px solid {sc};
                           border-radius:4px;'>
                <b>{b['name']}</b><br>
                🌡 {b.get('temp','—')}° &nbsp; 💧{b.get('hum','—')}% &nbsp; 🌬{b.get('wind','—')} מ"ש<br>
                {b.get('status','—')}
                </div>""",
            sticky=True
        )
    ).add_to(m)
    folium.Marker(
        [b["lat"], b["lon"]],
        icon=folium.DivIcon(html=f"""
        <div style="color:{sc}; font-family:'Heebo',sans-serif; font-weight:bold;
                    font-size:12px; white-space:nowrap; margin-top:-28px;
                    text-shadow:0 0 6px {sc}, 0 0 12px {sc}77; letter-spacing:1px;">
        {b['name']}
        </div>
        """)
    ).add_to(m)

map_data = st_folium(m, width="100%", height=520)

# ── Weather for clicked map location ──
if map_data and map_data.get("last_clicked"):
    clat = map_data["last_clicked"]["lat"]
    clon = map_data["last_clicked"]["lng"]

    # Check if clicked near an existing base
    clicked_base = next(
        (b for b in st.session_state.bases
         if abs(b["lat"] - clat) < 0.08 and abs(b["lon"] - clon) < 0.08),
        None
    )
    location_name = clicked_base["name"] if clicked_base else f"{clat:.3f}°N, {clon:.3f}°E"

    st.markdown("""
    <div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
                color:rgba(0,255,156,0.6); letter-spacing:1px; margin:16px 0 8px;
                border-right:3px solid #00ff9c; padding-right:10px;">
        📍 מזג אוויר עבור המיקום שנבחר
    </div>
    """, unsafe_allow_html=True)

    wr = get_weather_by_coords(clat, clon)
    if "main" in wr:
        wt   = wr["main"]["temp"]
        wh   = wr["main"]["humidity"]
        ww   = wr["wind"]["speed"]
        wwd  = wr["wind"].get("deg", 0)
        wdesc= wr["weather"][0].get("description", "")
        ws   = status(wt, ww, wh)
        st.markdown(render_current_weather(
            location_name, wt, wh, ww, wwd, wdesc, ws,
            is_base=bool(clicked_base), lat=clat, lon=clon
        ), unsafe_allow_html=True)
        # 7-day forecast for clicked location
        fc = get_forecast_by_coords(clat, clon)
        daily = build_daily_forecast(fc)
        st.markdown(render_forecast(daily), unsafe_allow_html=True)

st.markdown("<hr style='border-color:rgba(0,255,156,0.1); margin:20px 0;'>", unsafe_allow_html=True)

# ================== BASE TABLE ==================
if st.session_state.bases:
    st.markdown("""
    <div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
                color:rgba(0,255,156,0.6); letter-spacing:1px; margin-bottom:14px;
                border-right:3px solid #00ff9c; padding-right:10px;">
        ◉ בסיסים פעילים — מצב מזג אוויר
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(min(len(st.session_state.bases), 3))
    for i, b in enumerate(st.session_state.bases):
        sc = status_color_hex(b.get("status", "🟢"))
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.45); border:1px solid {sc}33;
                        border-top:3px solid {sc}; border-radius:8px; padding:16px;
                        margin-bottom:12px; direction:rtl; transition: all 0.2s;">
                <div style="font-family:'Heebo',sans-serif; font-size:16px; font-weight:700;
                            color:{sc}; margin-bottom:10px;">
                    {b['name']}
                </div>
                <div style="font-family:'Heebo',sans-serif; font-size:13px;
                            line-height:2.0; color:rgba(200,255,230,0.85);">
                    🌡️ {b.get('temp','—')}°C &nbsp;&nbsp;
                    💧 {b.get('hum','—')}% &nbsp;&nbsp;
                    🌬️ {b.get('wind','—')} מ"ש
                </div>
                <div style="margin-top:8px; font-family:'Heebo',sans-serif; font-weight:700;
                            font-size:13px; color:{sc}; text-shadow:0 0 8px {sc};">
                    {b.get('status','—')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================== ADMIN PANEL ==================
if is_admin:
    st.markdown("""
    <div style="background:rgba(0,255,156,0.03); border:1px solid rgba(0,255,156,0.2);
                border-radius:10px; padding:24px; margin-top:24px;">
        <div style="font-family:'Heebo',sans-serif; font-size:18px; font-weight:700;
                    color:#00ff9c; letter-spacing:2px; margin-bottom:18px; text-align:center;
                    border-bottom:1px solid rgba(0,255,156,0.15); padding-bottom:12px;">
            ⬡ לוח בקרת מנהל ⬡
        </div>
    """, unsafe_allow_html=True)

    tab_add, tab_del, tab_edit = st.tabs(["➕ הוסף בסיס", "❌ מחק בסיס", "✏️ ערוך בסיס"])

    with tab_add:
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            st.markdown(f"""
            <div style="font-family:'Heebo',sans-serif; font-size:13px;
                        color:rgba(0,255,156,0.6); margin-bottom:12px; direction:rtl;">
                📍 מיקום נבחר: {lat:.5f}°N · {lon:.5f}°E
            </div>
            """, unsafe_allow_html=True)
            name = st.text_input("שם הבסיס", placeholder="הזן שם...", key="add_name")
            if st.button("➕ הוסף בסיס", use_container_width=True):
                if name:
                    w = get_weather_by_coords(lat, lon)
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
            st.info("🗺️ לחץ על המפה כדי לבחור מיקום לבסיס חדש")

    with tab_del:
        if st.session_state.bases:
            names   = [b["name"] for b in st.session_state.bases]
            sel_del = st.selectbox("בחר בסיס למחיקה", names, key="del_select")
            if st.button("❌ מחק בסיס", use_container_width=True):
                st.session_state.bases = [b for b in st.session_state.bases if b["name"] != sel_del]
                save_bases(st.session_state.bases)
                st.success(f"🗑️ בסיס '{sel_del}' נמחק")
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
<div style="text-align:center; padding:30px 0 10px; font-family:'Heebo',sans-serif;
            font-size:11px; color:rgba(0,255,156,0.2); letter-spacing:2px; direction:rtl;">
    המל שמי שליטה · סווג · כל הזכויות שמורות · HAMAL SKY CONTROL · CLASSIFIED
</div>
""", unsafe_allow_html=True)
