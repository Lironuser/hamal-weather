# "streamlit run app.py" - To start the app.

import streamlit as st
import altair as alt
import requests
import pandas as pd
import time
import json
import io
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from deep_translator import GoogleTranslator
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter
from fpdf import FPDF
from bidi.algorithm import get_display

# ===== CONFIG =====
API_KEY      = "c88dbf32015479ed56b386340beff25d"
DATA_FILE    = "bases.json"
HISTORY_FILE = "history.json"
ALERTS_FILE  = "alerts.json"
URL          = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ONECALL_URL  = "https://api.openweathermap.org/data/3.0/onecall"
FONT_DIR     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_PATH    = os.path.join(FONT_DIR, "NotoSansHebrew-Variable.ttf")

DEFAULT_TH_TEMP = 35
DEFAULT_TH_WIND = 10
DEFAULT_TH_HUM  = 85

st.set_page_config(page_title="Hamal sky control", layout="wide", page_icon="🛰️")

# ===== GLOBAL STYLES =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Heebo:wght@300;400;500;600;700;900&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --primary:   #6be0c8;
    --secondary: #5b7fff;
    --danger:    #ff5f6b;
    --warning:   #ff9d6b;
    --dark:      #05070d;
    --panel:     rgba(0, 255, 156, 0.04);
    --border:    rgba(0, 255, 156, 0.18);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    color: #e8ecf5 !important;
    font-family: 'Heebo', sans-serif !important;
    direction: rtl;
}

[data-testid="stSidebar"] {
    background: #070a14 !important;
    border-right: none !important;
    border-left: 1px solid var(--border) !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(107,224,200,0.012) 2px,
        rgba(107,224,200,0.012) 4px
    );
    pointer-events: none;
    z-index: 9998;
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: var(--primary) !important;
    text-shadow: 0 0 20px rgba(107,224,200,0.6), 0 0 40px rgba(107,224,200,0.2) !important;
    letter-spacing: 2px !important;
}

input, textarea, select {
    background: rgba(107,224,200,0.06) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--primary) !important;
    font-family: 'Heebo', sans-serif !important;
    caret-color: var(--primary) !important;
}
input:focus, textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 12px rgba(107,224,200,0.3) !important;
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
    background: linear-gradient(135deg, rgba(107,224,200,0.12), rgba(107,224,200,0.04)) !important;
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
    background: rgba(107,224,200,0.2) !important;
    box-shadow: 0 0 20px rgba(107,224,200,0.4), inset 0 0 15px rgba(107,224,200,0.1) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stSuccess"] {
    background: rgba(107,224,200,0.08) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 4px !important;
    color: var(--primary) !important;
    font-family: 'Heebo', sans-serif !important;
}
[data-testid="stError"] {
    background: rgba(255,95,107,0.08) !important;
    border: 1px solid var(--danger) !important;
    color: var(--danger) !important;
    font-family: 'Heebo', sans-serif !important;
}
[data-testid="stWarning"] {
    background: rgba(255,157,107,0.08) !important;
    border: 1px solid var(--warning) !important;
    color: var(--warning) !important;
    font-family: 'Heebo', sans-serif !important;
}

[data-testid="stSidebar"] * {
    font-family: 'Heebo', sans-serif !important;
    color: #e8ecf5 !important;
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
    color: rgba(107,224,200,0.6) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--primary) !important;
    text-shadow: 0 0 10px rgba(107,224,200,0.5) !important;
}

hr { border-color: var(--border) !important; margin: 20px 0 !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

[data-testid="stSelectbox"] > div > div {
    background: rgba(107,224,200,0.06) !important;
    border: 1px solid var(--border) !important;
    color: var(--primary) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(107,224,200,0.04) !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: rgba(107,224,200,0.5) !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
}

[data-testid="stInfo"] {
    background: rgba(91,127,255,0.06) !important;
    border: 1px solid rgba(91,127,255,0.25) !important;
    color: #5b7fff !important;
    font-family: 'Heebo', sans-serif !important;
}

[data-testid="stDialog"] [role="dialog"] {
    background: #05070d !important;
    border: 1px solid rgba(107,224,200,0.25) !important;
}
[data-testid="stDialog"] * {
    color: #e8ecf5;
}
[data-testid="stDialog"] h1 {
    font-family: 'Heebo', sans-serif !important;
    color: #6be0c8 !important;
    text-shadow: none !important;
    font-size: 18px !important;
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

# ===== HISTORY LOG (for trends) =====
def load_history():
    try:
        return json.load(open(HISTORY_FILE, encoding="utf-8"))
    except Exception:
        return []

def save_history(h):
    # keep the log bounded so the file doesn't grow forever
    json.dump(h[-4000:], open(HISTORY_FILE, "w", encoding="utf-8"), ensure_ascii=False)

def log_history(base_name, temp, hum, wind, status_str):
    h = load_history()
    h.append({
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base": base_name,
        "temp": temp, "hum": hum, "wind": wind,
        "status": strip_status_icon(status_str),
    })
    save_history(h)

# ===== ALERTS LOG + EMAIL =====
def load_alerts():
    try:
        return json.load(open(ALERTS_FILE, encoding="utf-8"))
    except Exception:
        return []

def save_alerts(a):
    json.dump(a[-1000:], open(ALERTS_FILE, "w", encoding="utf-8"), ensure_ascii=False)

def send_email_alert(base_name, new_status):
    """Best-effort email notification. Silently does nothing if SMTP isn't
    configured in st.secrets — this lets the app run fine without email set up."""
    try:
        cfg = st.secrets["smtp"]
    except Exception:
        return
    try:
        msg = MIMEText(f"בסיס {base_name} עבר למצב: {new_status}", "plain", "utf-8")
        msg["Subject"] = f"HAMAL ALERT: {base_name} - {new_status}"
        msg["From"] = cfg["from_addr"]
        msg["To"]   = cfg["to_addr"]
        with smtplib.SMTP(cfg["host"], int(cfg.get("port", 587)), timeout=8) as server:
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["from_addr"], [cfg["to_addr"]], msg.as_string())
    except Exception as e:
        st.session_state["_last_email_error"] = str(e)

def log_alert(base_name, from_status, to_status):
    a = load_alerts()
    a.append({
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base": base_name, "from": from_status, "to": to_status,
    })
    save_alerts(a)
    send_email_alert(base_name, to_status)

def refresh_all_bases():
    """Pulls fresh weather for every saved base, updates it in place,
    appends a history record, and raises alerts for any base that just
    crossed into 'מסוכן'. Returns the list of base names that newly alerted."""
    newly_dangerous = []
    for b in st.session_state.bases:
        w = get_weather_by_coords(b["lat"], b["lon"])
        if "main" not in w:
            continue
        t, h, wd = w["main"]["temp"], w["main"]["humidity"], w["wind"]["speed"]
        th_t = b.get("th_temp", DEFAULT_TH_TEMP)
        th_w = b.get("th_wind", DEFAULT_TH_WIND)
        th_h = b.get("th_hum",  DEFAULT_TH_HUM)
        old_status_raw = strip_status_icon(b.get("status", ""))
        new_status     = status_with_icon(t, wd, h, th_t, th_w, th_h)
        new_status_raw = strip_status_icon(new_status)

        if new_status_raw == "מסוכן" and old_status_raw != "מסוכן":
            log_alert(b["name"], old_status_raw or "—", new_status_raw)
            newly_dangerous.append(b["name"])

        b["temp"], b["hum"], b["wind"] = t, h, wd
        b["status"] = new_status
        b["color"]  = color(new_status)
        log_history(b["name"], t, h, wd, new_status)

    save_bases(st.session_state.bases)
    return newly_dangerous

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

def build_daily_forecast_onecall(data):
    """Builds the same daily dict shape as build_daily_forecast(), but from
    the One Call 3.0 'daily' block, which gives real per-day min/max/avg
    values for up to 8 days - no 3-hour-bucket guessing needed."""
    result = []
    for day in data.get("daily", [])[:8]:
        dt_str = datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d %H:%M:%S")
        desc = day["weather"][0]["description"]
        s = status_with_icon(day["temp"]["max"], day.get("wind_speed", 0), day["humidity"])
        result.append({
            "date": dt_str[:10],
            "label": format_date_he(dt_str),
            "temp_max": round(day["temp"]["max"]),
            "temp_min": round(day["temp"]["min"]),
            "wind_avg": round(day.get("wind_speed", 0), 1),
            "wind_max": round(day.get("wind_gust", day.get("wind_speed", 0)), 1),
            "hum_avg": round(day["humidity"]),
            "hum_max": round(day["humidity"]),
            "desc": desc,
            "icon": weather_icon(desc),
            "status": s,
        })
    return result

def get_daily_forecast(lat, lon):
    """Real forecast fetcher with a graceful fallback.
    Tries One Call 3.0 first, which gives a genuine 7-8 day daily forecast.
    That endpoint needs a subscription-enabled API key though, so if it's
    unavailable (401/403, or the key just isn't enrolled) we fall back to
    the free 5-day/3-hour endpoint and build daily buckets from that instead.
    Returns (daily_list, source) where source is "onecall" or "5day" so the
    UI can be honest about which one was actually used."""
    try:
        r = requests.get(ONECALL_URL, params={
            "lat": lat, "lon": lon, "appid": API_KEY, "units": "metric",
            "exclude": "current,minutely,hourly,alerts",
        }, timeout=8).json()
        if "daily" in r and r["daily"]:
            return build_daily_forecast_onecall(r), "onecall"
    except Exception:
        pass
    fc = get_forecast_by_coords(lat, lon)
    return build_daily_forecast(fc), "5day"

def forecast_source_caption(source, n_days):
    if source == "onecall":
        return f"✅ תחזית מלאה ({n_days} ימים, One Call API)"
    return f"⚠️ תחזית מוגבלת ל-{n_days} ימים — המפתח הנוכחי לא רשום ל-One Call 3.0, נופל חזרה לתחזית 3 שעות/5 ימים"

def status(temp, wind, hum, th_temp=DEFAULT_TH_TEMP, th_wind=DEFAULT_TH_WIND, th_hum=DEFAULT_TH_HUM):
    score = (temp > th_temp) * 2 + (wind > th_wind) * 2 + (hum > th_hum)
    return "מסוכן" if score >= 4 else "בינוני" if score >= 2 else "תקין"

def status_with_icon(temp, wind, hum, th_temp=DEFAULT_TH_TEMP, th_wind=DEFAULT_TH_WIND, th_hum=DEFAULT_TH_HUM):
    s = status(temp, wind, hum, th_temp, th_wind, th_hum)
    return f"🔴 {s}" if s == "מסוכן" else f"🟡 {s}" if s == "בינוני" else f"🟢 {s}"

def strip_status_icon(s):
    return s.replace("🔴 ", "").replace("🟡 ", "").replace("🟢 ", "").strip()

def status_color_hex(s):
    return "#ff5f6b" if "מסוכן" in s else "#ff9d6b" if "בינוני" in s else "#6be0c8"

def color(s):
    return "red" if "מסוכן" in s else "orange" if "בינוני" in s else "green"

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
    # NOTE: the free OpenWeatherMap "5 day / 3 hour" endpoint only ever
    # returns ~5 calendar days of data (40 x 3h records). We used to always
    # slice to [:7] and call it "weekly", which was misleading and made the
    # last 1-2 "days" look broken/missing. We now only keep days that have
    # enough real samples and report however many full days actually exist.
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
        # Skip days with too few 3-hour samples (e.g. a sliver of "today"
        # right before midnight, or a partial final day) - their min/max
        # would be misleading rather than a real daily picture.
        if len(items) < 3:
            continue
        temps = [i["main"]["temp"] for i in items]
        winds = [i["wind"]["speed"] for i in items]
        hums  = [i["main"]["humidity"] for i in items]
        descs = [i["weather"][0]["description"] for i in items]
        noon_items = [i for i in items if "12:00" in i["dt_txt"] or "15:00" in i["dt_txt"]]
        main_desc = noon_items[0]["weather"][0]["description"] if noon_items else descs[len(descs)//2]
        s = status_with_icon(max(temps), max(winds), max(hums))
        result.append({
            "date": date_str,
            "label": format_date_he(items[len(items)//2]["dt_txt"]),
            "temp_max": round(max(temps)),
            "temp_min": round(min(temps)),
            "wind_avg": round(sum(winds)/len(winds), 1),
            "wind_max": round(max(winds), 1),
            "hum_avg":  round(sum(hums)/len(hums)),
            "hum_max":  round(max(hums)),
            "desc": main_desc,
            "icon": weather_icon(main_desc),
            "status": s,
        })
    return result[:7]

def generate_pdf_report(bases):
    """Consolidated daily PDF report for all bases, right-to-left Hebrew table."""
    def rtl(t):
        return get_display(str(t))

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Hebrew", "", FONT_PATH)
    pdf.set_font("Hebrew", size=17)
    pdf.set_text_color(20, 25, 40)
    pdf.cell(0, 12, rtl("דוח מזג אוויר יומי — חמל שמי שליטה"), new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.set_font("Hebrew", size=10)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 8, rtl(f"נוצר: {datetime.now().strftime('%d/%m/%Y  %H:%M')}"), new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(4)

    headers = ["בסיס", "טמפ' (°C)", "לחות (%)", "רוח (מ/ש)", "סטטוס", "קואורדינטות"]
    col_w   = [45, 25, 25, 25, 35, 35]

    pdf.set_font("Hebrew", size=11)
    pdf.set_fill_color(20, 25, 40)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(reversed(headers)):
        pdf.cell(list(reversed(col_w))[i], 9, rtl(h), border=1, align="C", fill=True)
    pdf.ln(9)

    pdf.set_font("Hebrew", size=10)
    pdf.set_text_color(20, 20, 20)
    status_fill = {"מסוכן": (255, 224, 224), "בינוני": (255, 243, 214), "תקין": (224, 245, 235)}
    for idx, b in enumerate(bases):
        raw_status = strip_status_icon(b.get("status", "—"))
        vals = [
            b["name"],
            str(b.get("temp", "—")),
            str(b.get("hum", "—")),
            str(b.get("wind", "—")),
            raw_status,
            f'{b["lat"]:.3f}, {b["lon"]:.3f}',
        ]
        base_fill = status_fill.get(raw_status, (245, 245, 250) if idx % 2 == 0 else (255, 255, 255))
        pdf.set_fill_color(*base_fill)
        for i, v in enumerate(reversed(vals)):
            pdf.cell(list(reversed(col_w))[i], 8, rtl(v), border=1, align="C", fill=True)
        pdf.ln(8)

    danger = sum(1 for b in bases if strip_status_icon(b.get("status", "")) == "מסוכן")
    warn   = sum(1 for b in bases if strip_status_icon(b.get("status", "")) == "בינוני")
    ok     = sum(1 for b in bases if strip_status_icon(b.get("status", "")) == "תקין")

    pdf.ln(6)
    pdf.set_font("Hebrew", size=12)
    pdf.set_text_color(20, 25, 40)
    pdf.cell(0, 8, rtl(f"סיכום: {ok} תקין  |  {warn} בינוני  |  {danger} מסוכן  מתוך {len(bases)} בסיסים"),
             new_x="LMARGIN", new_y="NEXT", align="R")

    recent_alerts = load_alerts()[-10:]
    if recent_alerts:
        pdf.ln(6)
        pdf.set_font("Hebrew", size=13)
        pdf.cell(0, 9, rtl("התראות אחרונות"), new_x="LMARGIN", new_y="NEXT", align="R")
        pdf.set_font("Hebrew", size=9)
        pdf.set_text_color(90, 90, 90)
        for a in reversed(recent_alerts):
            pdf.cell(0, 7, rtl(f"{a['ts']}  ·  {a['base']}  ·  {a['from']} ← {a['to']}"),
                     new_x="LMARGIN", new_y="NEXT", align="R")

    return bytes(pdf.output())


def create_forecast_excel(base_name: str, lat: float, lon: float, daily_list: list) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = f"תחזית {len(daily_list)} ימים"

    # --- color palette ---
    C_BG       = "0D1117"
    C_HEADER   = "161B22"
    C_ACCENT   = "00C875"   # green accent
    C_BLUE     = "58A6FF"
    C_YELLOW   = "F0A500"
    C_RED      = "FF4C4C"
    C_TEXT     = "E6EDF3"
    C_SUBTEXT  = "8B949E"
    C_ROW_ALT  = "0D2015"
    C_ROW_NORM = "0A1A0E"

    thin = Side(style="thin", color="2D3A2E")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def cell(ws, row, col, value, bold=False, size=11, color=C_TEXT,
             bg=None, align="center", wrap=False):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", bold=bold, size=size, color=color)
        c.alignment = Alignment(
            horizontal="center",
            vertical="center",
            readingOrder=2
        )
        if bg:
            c.fill = PatternFill("solid", fgColor=bg)
        c.border = border
        return c

    # ── Row 1: Title ──
    ws.merge_cells("A1:H1")
    c = ws["A1"]
    c.value = f"תחזית מזג אוויר ל-{len(daily_list)} ימים  |  {base_name}"
    c.font = Font(name="Arial", bold=True, size=16, color=C_ACCENT)
    c.fill = PatternFill("solid", fgColor=C_HEADER)
    c.alignment = Alignment(horizontal="center", vertical="center", readingOrder=2)
    c.border = border
    ws.row_dimensions[1].height = 36

    # ── Row 2: Meta info ──
    ws.merge_cells("A2:D2")
    c2 = ws["A2"]
    c2.value = f"קואורדינטות: {lat:.4f}N  |  {lon:.4f}E"
    c2.font = Font(name="Arial", size=10, color=C_SUBTEXT)
    c2.fill = PatternFill("solid", fgColor=C_HEADER)
    c2.alignment = Alignment(horizontal="right", vertical="center", readingOrder=2)

    ws.merge_cells("E2:H2")
    c3 = ws["E2"]
    c3.value = f"נוצר: {datetime.now().strftime('%d/%m/%Y  %H:%M')}"
    c3.font = Font(name="Arial", size=10, color=C_SUBTEXT)
    c3.fill = PatternFill("solid", fgColor=C_HEADER)
    c3.alignment = Alignment(horizontal="left", vertical="center", readingOrder=2)
    ws.row_dimensions[2].height = 22

    # ── Row 3: blank divider ──
    for col in range(1, 9):
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=C_BG)
    ws.row_dimensions[3].height = 8

    # ── Row 4: Column headers ──
    headers = ["תאריך", "יום", "מזג אוויר", "טמפ מקס (°C)", "טמפ מינ (°C)",
               "לחות ממוצעת (%)", "רוח ממוצעת (מ/ש)", "סטטוס"]
    for col, h in enumerate(headers, 1):
        cell(ws, 4, col, h, bold=True, size=11, color=C_ACCENT, bg=C_HEADER)
    ws.row_dimensions[4].height = 28

    # ── Rows 5+: Data ──
    status_colors = {"תקין": C_ACCENT, "בינוני": C_YELLOW, "מסוכן": C_RED}

    for i, d in enumerate(daily_list):
        row = i + 5
        bg = C_ROW_ALT if i % 2 == 0 else C_ROW_NORM

        # Strip emoji from status for clean export
        raw_status = d["status"].replace("🔴 ", "").replace("🟡 ", "").replace("🟢 ", "")
        sc = status_colors.get(raw_status, C_TEXT)

        # date parts
        date_obj = datetime.strptime(d["date"], "%Y-%m-%d")
        date_str = date_obj.strftime("%d/%m/%Y")
        day_name = DAYS_HE[date_obj.weekday()]

        cell(ws, row, 1, date_str,    bg=bg, color=C_TEXT)
        cell(ws, row, 2, day_name,    bg=bg, color=C_BLUE, bold=True)
        cell(ws, row, 3, d["desc"].title(), bg=bg, color=C_SUBTEXT, align="right", wrap=True)
        cell(ws, row, 4, d["temp_max"], bg=bg, color=C_RED   if d["temp_max"] > 35 else C_TEXT, bold=True)
        cell(ws, row, 5, d["temp_min"], bg=bg, color=C_BLUE,  bold=False)
        cell(ws, row, 6, d["hum_avg"],  bg=bg, color=C_BLUE)
        cell(ws, row, 7, d["wind_avg"], bg=bg,
             color=C_RED if d["wind_avg"] > 10 else C_TEXT)
        cell(ws, row, 8, raw_status,    bg=bg, color=sc, bold=True)
        ws.row_dimensions[row].height = 24

    # ── Row after data: summary ──
    last_data_row = 4 + len(daily_list)
    summary_row = last_data_row + 2
    ws.merge_cells(f"A{summary_row}:H{summary_row}")
    sc = ws.cell(row=summary_row, column=1,
                 value="סיכום שבועי")
    sc.font = Font(name="Arial", bold=True, size=11, color=C_ACCENT)
    sc.fill = PatternFill("solid", fgColor=C_HEADER)
    sc.alignment = Alignment(horizontal="center", vertical="center", readingOrder=2)
    sc.border = border
    ws.row_dimensions[summary_row].height = 26

    # summary data labels + formulas
    sum_labels = [
        ("טמפרטורה מקסימלית בשבוע", f"=MAX(D5:D{last_data_row})", C_RED),
        ("טמפרטורה מינימלית בשבוע", f"=MIN(E5:E{last_data_row})", C_BLUE),
        ("לחות ממוצעת בשבוע",        f"=AVERAGE(F5:F{last_data_row})", C_BLUE),
        ("מהירות רוח מקסימלית",      f"=MAX(G5:G{last_data_row})", C_YELLOW),
    ]
    for j, (lbl, formula, fc) in enumerate(sum_labels):
        r = summary_row + 1 + j
        cell(ws, r, 1, lbl,     bg=C_ROW_NORM, color=C_SUBTEXT, align="right", bold=False)
        ws.merge_cells(f"A{r}:G{r}")
        c_val = ws.cell(row=r, column=8, value=formula)
        c_val.font = Font(name="Arial", bold=True, size=12, color=fc)
        c_val.fill = PatternFill("solid", fgColor=C_ROW_NORM)
        c_val.alignment = Alignment(horizontal="center", vertical="center", readingOrder=2)
        c_val.border = border
        ws.row_dimensions[r].height = 22

    # ── Column widths ──
    col_widths = [13, 10, 26, 16, 16, 20, 22, 12]
    for col, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = w

    # ── Freeze panes below header ──
    ws.freeze_panes = "A5"

    # ── Sheet background (fill all unused cells) ──
    for row in ws.iter_rows(min_row=1, max_row=summary_row + 6,
                             min_col=1, max_col=8):
        for c in row:
            if c.fill.fgColor.rgb in ("00000000", "000000"):
                c.fill = PatternFill("solid", fgColor=C_BG)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()

def render_current_weather(name, temp, hum, wind, wdir, desc, s, is_base=True, lat=None, lon=None):
    scolor = status_color_hex(s)
    border_color = scolor if is_base else "#5b7fff"
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
                            color:rgba(107,224,200,0.4); margin-top:4px;">
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
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(107,224,200,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">🌡️</div>
                <div style="font-family:'Orbitron',monospace; font-size:20px; color:#6be0c8; font-weight:700;">{temp}°</div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(107,224,200,0.5);">טמפרטורה °C</div>
            </div>
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(91,127,255,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">💧</div>
                <div style="font-family:'Orbitron',monospace; font-size:20px; color:#5b7fff; font-weight:700;">{hum}%</div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(91,127,255,0.5);">לחות</div>
            </div>
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(255,157,107,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">🌬️</div>
                <div style="font-family:'Orbitron',monospace; font-size:20px; color:#ff9d6b; font-weight:700;">{wind}</div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(255,157,107,0.5);">רוח מ/ש</div>
            </div>
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(232,236,245,0.1);
                        border-radius:6px; padding:12px; text-align:center;">
                <div style="font-size:24px;">🧭</div>
                <div style="font-family:'Orbitron',monospace; font-size:16px; color:#e8ecf5; font-weight:700;">
                    {wind_direction_arrow(wdir)}
                </div>
                <div style="font-family:'Heebo',sans-serif; font-size:11px;
                            color:rgba(232,236,245,0.5);">כיוון רוח</div>
            </div>
        </div>
        <div style="margin-top:12px; font-family:'Heebo',sans-serif; font-size:13px;
                    color:rgba(107,224,200,0.5); text-align:center; letter-spacing:1px;">
            {icon} {desc.upper()}
        </div>
    </div>
    """

def render_forecast(daily_list):
    if not daily_list:
        return ""
    n_days = len(daily_list)
    all_max = [d["temp_max"] for d in daily_list]
    all_min = [d["temp_min"] for d in daily_list]
    week_hi, week_lo = max(all_max), min(all_min)
    span = max(week_hi - week_lo, 1)

    cards = ""
    for idx, d in enumerate(daily_list):
        sc = status_color_hex(d["status"])
        is_today = idx == 0
        bar_top = round((week_hi - d["temp_max"]) / span * 100)
        bar_h   = max(round((d["temp_max"] - d["temp_min"]) / span * 100), 8)
        ring = f"box-shadow:0 0 0 1px {sc}, 0 8px 20px -6px {sc}66;" if is_today else f"box-shadow:0 4px 14px -8px {sc}55;"
        cards += f"""
        <div style="background:linear-gradient(180deg, {sc}14, rgba(0,0,0,0.35));
                    border:1px solid {sc}40; border-top:3px solid {sc}; border-radius:12px;
                    padding:16px 12px; text-align:center; min-width:112px; flex:1;
                    {ring}">
            <div style="font-family:'Heebo',sans-serif; font-size:12px; font-weight:700;
                        color:{'#e8ecf5' if is_today else 'rgba(232,236,245,0.6)'};
                        margin-bottom:8px; white-space:nowrap;">
                {'היום' if is_today else d['label']}
            </div>
            <div style="font-size:32px; margin:4px 0 8px; filter:drop-shadow(0 0 6px {sc}55);">{d['icon']}</div>
            <div style="font-family:'Orbitron',monospace; font-size:17px; color:#e8ecf5; font-weight:700;">
                {d['temp_max']}°
            </div>
            <div style="display:flex; align-items:center; justify-content:center; gap:6px; margin:6px 0;">
                <span style="font-family:'Heebo',sans-serif; font-size:11px; color:rgba(232,236,245,0.4);">{d['temp_min']}°</span>
                <span style="position:relative; width:5px; height:34px; border-radius:3px;
                             background:rgba(232,236,245,0.12); overflow:hidden; display:inline-block;">
                    <span style="position:absolute; top:{bar_top}%; height:{bar_h}%; width:100%;
                                 background:{sc}; border-radius:3px;"></span>
                </span>
                <span style="font-family:'Heebo',sans-serif; font-size:11px; color:rgba(232,236,245,0.4);">{d['temp_max']}°</span>
            </div>
            <div style="font-family:'Heebo',sans-serif; font-size:11px; color:rgba(91,127,255,0.75); margin-top:6px;">
                💧 {d['hum_avg']}%
            </div>
            <div style="font-family:'Heebo',sans-serif; font-size:11px; color:rgba(255,157,107,0.75);">
                🌬 {d['wind_avg']} מ"ש
            </div>
            <div style="display:inline-block; margin-top:10px; padding:3px 10px; border-radius:20px;
                        background:{sc}22; font-size:10px; color:{sc}; font-weight:700; letter-spacing:0.5px;">
                {d['status']}
            </div>
        </div>
        """
    return f"""
    <div style="margin-top:16px; direction:rtl;">
        <div style="font-family:'Heebo',sans-serif; font-size:13px; font-weight:700;
                    color:rgba(107,224,200,0.6); letter-spacing:2px; margin-bottom:10px;
                    border-right:3px solid var(--primary); padding-right:10px;">
            📅 תחזית ל-{n_days} ימים
        </div>
        <div style="display:flex; gap:10px; overflow-x:auto; padding-bottom:8px;">
            {cards}
        </div>
    </div>
    """

def build_forecast_chart(daily_list):
    """Builds a dark-themed temperature range chart (min-max band + max/min
    lines) for the forecast, plus a small humidity/wind bar chart below."""
    df = pd.DataFrame(daily_list)
    label_order = list(df["label"])

    axis_x = alt.Axis(labelColor="#c7cfe8", labelFontSize=12, domainColor="#2a3550",
                       tickColor="#2a3550", labelAngle=0)
    axis_y = alt.Axis(labelColor="#c7cfe8", titleColor="#c7cfe8",
                       gridColor="rgba(107,224,200,0.08)", domainColor="#2a3550")

    band = alt.Chart(df).mark_area(opacity=0.18, color="#6be0c8").encode(
        x=alt.X("label:N", sort=label_order, title=None, axis=axis_x),
        y=alt.Y("temp_min:Q", title="טמפרטורה (°C)", axis=axis_y),
        y2="temp_max:Q",
    )
    max_line = alt.Chart(df).mark_line(
        point=alt.OverlayMarkDef(color="#ff9d6b", size=70, filled=True),
        strokeWidth=3, color="#ff9d6b"
    ).encode(
        x=alt.X("label:N", sort=label_order),
        y="temp_max:Q",
        tooltip=[alt.Tooltip("label:N", title="יום"),
                 alt.Tooltip("temp_max:Q", title="מקס׳ °C"),
                 alt.Tooltip("temp_min:Q", title="מינ׳ °C")],
    )
    min_line = alt.Chart(df).mark_line(
        point=alt.OverlayMarkDef(color="#5b7fff", size=70, filled=True),
        strokeWidth=2, strokeDash=[5, 3], color="#5b7fff"
    ).encode(
        x=alt.X("label:N", sort=label_order),
        y="temp_min:Q",
    )

    temp_chart = (band + max_line + min_line).properties(height=260).configure_view(
        strokeWidth=0
    ).configure(background="transparent")

    return temp_chart

def build_humidity_wind_chart(daily_list):
    df = pd.DataFrame(daily_list)
    label_order = list(df["label"])
    axis_x = alt.Axis(labelColor="#c7cfe8", labelFontSize=11, domainColor="#2a3550",
                       tickColor="#2a3550", labelAngle=0)
    axis_y = alt.Axis(labelColor="#c7cfe8", titleColor="#c7cfe8",
                       gridColor="rgba(107,224,200,0.08)", domainColor="#2a3550")

    hum_bars = alt.Chart(df).mark_bar(color="#5b7fff", opacity=0.55, size=18).encode(
        x=alt.X("label:N", sort=label_order, title=None, axis=axis_x),
        y=alt.Y("hum_avg:Q", title="לחות (%)", axis=axis_y),
        tooltip=[alt.Tooltip("label:N", title="יום"), alt.Tooltip("hum_avg:Q", title="לחות %")],
    )
    wind_line = alt.Chart(df).mark_line(
        point=alt.OverlayMarkDef(color="#ff9d6b", size=50, filled=True),
        strokeWidth=2, color="#ff9d6b"
    ).encode(
        x=alt.X("label:N", sort=label_order),
        y=alt.Y("wind_avg:Q", title="רוח (מ/ש)", axis=alt.Axis(
            labelColor="#ff9d6b", titleColor="#ff9d6b", grid=False)),
        tooltip=[alt.Tooltip("label:N", title="יום"), alt.Tooltip("wind_avg:Q", title="רוח מ/ש")],
    )
    chart = alt.layer(hum_bars, wind_line).resolve_scale(y="independent").properties(
        height=180
    ).configure_view(strokeWidth=0).configure(background="transparent")
    return chart

@st.dialog("📅 תחזית מזג אוויר", width="large")
def show_forecast_dialog(base):
    sc = status_color_hex(base.get("status", "תקין"))
    st.markdown(f"""
    <div style="direction:rtl; margin-bottom:4px;">
        <div style="font-family:'Orbitron',monospace; font-size:20px; color:{sc}; letter-spacing:1px;">
            📍 {base['name']}
        </div>
        <div style="font-family:'Heebo',sans-serif; font-size:12px; color:rgba(232,236,245,0.45); margin-top:2px;">
            {base['lat']:.4f}°N · {base['lon']:.4f}°E
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("שולף תחזית עדכנית..."):
        daily, source = get_daily_forecast(base["lat"], base["lon"])

    if not daily:
        st.error("לא הצלחתי לקבל תחזית עבור בסיס זה כרגע. נסי שוב בעוד רגע.")
        if st.button("סגור", use_container_width=True, key="dlg_close_empty"):
            st.rerun()
        return

    tab_cards, tab_chart = st.tabs(["🗂️ כרטיסים", "📈 גרף"])
    with tab_cards:
        st.markdown(render_forecast(daily), unsafe_allow_html=True)
    with tab_chart:
        st.altair_chart(build_forecast_chart(daily), use_container_width=True)
        st.altair_chart(build_humidity_wind_chart(daily), use_container_width=True)
    st.caption(forecast_source_caption(source, len(daily)))

    excel_bytes = create_forecast_excel(base["name"], base["lat"], base["lon"], daily)
    dl_col, close_col = st.columns([3, 1])
    with dl_col:
        st.download_button(
            label=f"📥 ייצוא תחזית ל-Excel",
            data=excel_bytes,
            file_name=f"forecast_{base['name']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dlg_dl_excel"
        )
    with close_col:
        if st.button("✕ סגור", use_container_width=True, key="dlg_close"):
            st.rerun()

# ===== STATE =====
if "bases"               not in st.session_state: st.session_state.bases               = load_bases()
if "admin_mode"          not in st.session_state: st.session_state.admin_mode          = False
if "admin_anim"          not in st.session_state: st.session_state.admin_anim          = False
if "loaded"              not in st.session_state: st.session_state.loaded              = False
if "map_weather"         not in st.session_state: st.session_state.map_weather         = None
if "history_base"        not in st.session_state: st.session_state.history_base        = None
if "new_alerts"          not in st.session_state: st.session_state.new_alerts          = []

# ================== SPLASH SCREEN ==================
if not st.session_state.loaded:
    splash = st.empty()
    splash.markdown("""
    <style>
    .splash {
        position: fixed; top:0; left:0; width:100%; height:100%;
        background: radial-gradient(ellipse at center, #070b18 0%, #000000 100%);
        display:flex; flex-direction:column; justify-content:center; align-items:center;
        z-index:9999;
    }
    .sat { font-size:80px; animation: orbit 2.5s linear infinite; }
    .splash-title {
        color:#6be0c8; font-size:48px; font-weight:900;
        font-family:'Orbitron',monospace; letter-spacing:6px; margin-top:24px;
        text-shadow: 0 0 30px #6be0c8, 0 0 60px rgba(107,224,200,0.3);
    }
    .splash-he {
        color:rgba(107,224,200,0.7); font-size:22px; font-family:'Heebo',sans-serif;
        font-weight:700; letter-spacing:3px; margin-top:10px;
    }
    .splash-sub {
        color:rgba(107,224,200,0.4); font-size:13px;
        font-family:'Heebo',sans-serif; letter-spacing:4px; margin-top:8px;
        animation: blink 1.5s step-end infinite;
    }
    .radar {
        position:absolute; width:300px; height:300px;
        border-radius:50%; border:1px solid rgba(107,224,200,0.15);
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
    if st.session_state.bases:
        st.session_state.new_alerts = refresh_all_bases()

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 12px;">
        <div style="font-family:'Orbitron',monospace; font-size:13px; color:#6be0c8;
                    letter-spacing:4px; text-shadow:0 0 10px #6be0c8;">
            ⬡ חמל ⬡
        </div>
        <div style="font-family:'Heebo',sans-serif; font-size:11px;
                    color:rgba(107,224,200,0.4); letter-spacing:2px; margin-top:4px;">
            מערכת שמי שליטה · v2.3
        </div>
    </div>
    <hr style="border-color:rgba(107,224,200,0.15); margin:8px 0 16px;">
    """, unsafe_allow_html=True)

    now = datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y")
    st.markdown(f"""
    <div style="text-align:center; font-family:'Heebo',sans-serif;
                font-size:12px; color:rgba(107,224,200,0.55); letter-spacing:1px;
                margin-bottom:16px;">
        🕐 {now}
    </div>
    """, unsafe_allow_html=True)

    total        = len(st.session_state.bases)
    danger_count = sum(1 for b in st.session_state.bases if "מסוכן" in b.get("status",""))
    warn_count   = sum(1 for b in st.session_state.bases if "בינוני" in b.get("status",""))
    ok_count     = sum(1 for b in st.session_state.bases if "תקין"   in b.get("status",""))

    st.markdown(f"""
    <div style="background:rgba(107,224,200,0.04); border:1px solid rgba(107,224,200,0.15);
                border-radius:8px; padding:14px; margin-bottom:16px; direction:rtl;">
        <div style="font-family:'Heebo',sans-serif; font-size:13px; font-weight:700;
                    color:rgba(107,224,200,0.6); letter-spacing:1px; margin-bottom:10px;">
            סטטוס כללי
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#ff5f6b;">{danger_count}</div>
                <div style="font-size:10px; color:rgba(255,95,107,0.7); font-family:'Heebo',sans-serif;">מסוכן</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#ff9d6b;">{warn_count}</div>
                <div style="font-size:10px; color:rgba(255,157,107,0.7); font-family:'Heebo',sans-serif;">בינוני</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#6be0c8;">{ok_count}</div>
                <div style="font-size:10px; color:rgba(107,224,200,0.7); font-family:'Heebo',sans-serif;">תקין</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#e8ecf5;">{total}</div>
                <div style="font-size:10px; color:rgba(232,236,245,0.5); font-family:'Heebo',sans-serif;">סה"כ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(107,224,200,0.1);'>", unsafe_allow_html=True)

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
        <div style="background:rgba(107,224,200,0.08); border:1px solid rgba(107,224,200,0.35);
                    border-radius:6px; padding:12px; text-align:center; margin-bottom:10px;">
            <span style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
                         color:#6be0c8; letter-spacing:1px;">
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
        color:#6be0c8; font-size:40px; margin-top:18px;
        font-family:'Heebo',sans-serif; font-weight:900; letter-spacing:3px;
        text-shadow:0 0 20px #6be0c8, 0 0 40px rgba(107,224,200,0.4);
    }
    .access-sub {
        color:rgba(107,224,200,0.5); font-size:14px; margin-top:8px;
        font-family:'Heebo',sans-serif; letter-spacing:2px;
    }
    @keyframes pulse {
        0%,100% { transform:scale(1);   filter:drop-shadow(0 0 0px #6be0c8); }
        50%      { transform:scale(1.3); filter:drop-shadow(0 0 20px #6be0c8); }
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
            border-bottom:1px solid rgba(107,224,200,0.15); direction:rtl;">
    <div style="font-size:44px; filter:drop-shadow(0 0 12px #6be0c8);">🛰️</div>
    <div>
        <h1 style="margin:0; font-family:'Orbitron',monospace; font-size:26px; color:#6be0c8;
                   text-shadow:0 0 20px rgba(107,224,200,0.6), 0 0 40px rgba(107,224,200,0.2);
                   letter-spacing:4px;">
            HAMAL SKY CONTROL
        </h1>
        <div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:500;
                    color:rgba(107,224,200,0.5); letter-spacing:1px; margin-top:4px;">
            מערכת ניטור מזג אוויר מבצעי · ניטור בזמן אמת
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================== ALERT BANNER ==================
active_alerts = [b for b in st.session_state.bases if strip_status_icon(b.get("status", "")) == "מסוכן"]
if active_alerts:
    names = " · ".join(b["name"] for b in active_alerts)
    st.markdown(f"""
    <style>
    @keyframes alertPulse {{
        0%,100% {{ box-shadow: 0 0 0 0 rgba(255,95,107,0.35); }}
        50%      {{ box-shadow: 0 0 0 12px rgba(255,95,107,0); }}
    }}
    </style>
    <div style="background:rgba(255,95,107,0.1); border:1px solid #ff5f6b; border-radius:10px;
                padding:14px 18px; margin-bottom:20px; direction:rtl;
                animation: alertPulse 1.8s ease-in-out infinite;">
        <span style="color:#ff5f6b; font-family:'Heebo',sans-serif; font-weight:700; font-size:14px;
                     letter-spacing:0.5px;">
            🚨 {len(active_alerts)} בסיסים במצב מסוכן כרגע — {names}
        </span>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get("new_alerts"):
    for name in st.session_state.new_alerts:
        st.toast(f"🚨 התראה חדשה: {name} עבר למצב מסוכן", icon="🚨")
    st.session_state.new_alerts = []

# ================== SEARCH ==================
st.markdown("""
<div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
            color:rgba(107,224,200,0.6); letter-spacing:1px; margin-bottom:6px;
            border-right:3px solid #6be0c8; padding-right:10px;">
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
            s     = status_with_icon(temp, wind, hum)
            st.markdown(render_current_weather(
                found_base["name"], temp, hum, wind, wdir, desc, s,
                is_base=True, lat=found_base["lat"], lon=found_base["lon"]
            ), unsafe_allow_html=True)
            fc_daily, fc_source = get_daily_forecast(found_base["lat"], found_base["lon"])
            daily = fc_daily
            if daily:
                tab_cards1, tab_chart1 = st.tabs(["🗂️ כרטיסים", "📈 גרף"])
                with tab_cards1:
                    st.markdown(render_forecast(daily), unsafe_allow_html=True)
                with tab_chart1:
                    st.altair_chart(build_forecast_chart(daily), use_container_width=True)
                    st.altair_chart(build_humidity_wind_chart(daily), use_container_width=True)
                st.caption(forecast_source_caption(fc_source, len(daily)))
                excel_bytes = create_forecast_excel(
                    found_base["name"], found_base["lat"], found_base["lon"], daily
                )
                st.download_button(
                    label="📥 ייצוא תחזית ל-Excel",
                    data=excel_bytes,
                    file_name=f"forecast_{found_base['name']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_search_base"
                )
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
            s     = status_with_icon(temp, wind, hum)
            lat   = data["coord"]["lat"]
            lon   = data["coord"]["lon"]
            st.markdown(render_current_weather(
                city_en.upper(), temp, hum, wind, wdir, desc, s,
                is_base=False, lat=lat, lon=lon
            ), unsafe_allow_html=True)
            fc_daily, fc_source = get_daily_forecast(lat, lon)
            daily = fc_daily
            if daily:
                tab_cards2, tab_chart2 = st.tabs(["🗂️ כרטיסים", "📈 גרף"])
                with tab_cards2:
                    st.markdown(render_forecast(daily), unsafe_allow_html=True)
                with tab_chart2:
                    st.altair_chart(build_forecast_chart(daily), use_container_width=True)
                    st.altair_chart(build_humidity_wind_chart(daily), use_container_width=True)
                st.caption(forecast_source_caption(fc_source, len(daily)))
                excel_bytes = create_forecast_excel(city_en.upper(), lat, lon, daily)
                st.download_button(
                    label="📥 ייצוא תחזית ל-Excel",
                    data=excel_bytes,
                    file_name=f"forecast_{city_en}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_search_city"
                )
        else:
            st.error("❌ לא נמצא — בסיס או עיר לא ידועים")

st.markdown("<hr style='border-color:rgba(107,224,200,0.1); margin:16px 0 20px;'>", unsafe_allow_html=True)

# ================== MAP ==================
st.markdown("""
<div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
            color:rgba(107,224,200,0.6); letter-spacing:1px; margin-bottom:8px;
            border-right:3px solid #6be0c8; padding-right:10px;">
    🗺️ מפה טקטית — לחץ לבחירת מיקום
</div>
""", unsafe_allow_html=True)

m = folium.Map(location=[31.5, 34.8], zoom_start=7, tiles="CartoDB dark_matter")

for b in st.session_state.bases:
    sc = status_color_hex(b.get("status", "תקין"))
    folium.CircleMarker(
        location=[b["lat"], b["lon"]], radius=18,
        color=sc, fill=False, weight=1, opacity=0.35,
    ).add_to(m)
    folium.CircleMarker(
        location=[b["lat"], b["lon"]], radius=9,
        color=sc, fill=True, fill_color=sc, fill_opacity=0.85, weight=2,
        tooltip=folium.Tooltip(
            f"""<div style='font-family:monospace; font-size:13px; background:#070a14;
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

    clicked_base = next(
        (b for b in st.session_state.bases
         if abs(b["lat"] - clat) < 0.08 and abs(b["lon"] - clon) < 0.08),
        None
    )
    location_name = clicked_base["name"] if clicked_base else f"{clat:.3f}N, {clon:.3f}E"

    st.markdown("""
    <div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
                color:rgba(107,224,200,0.6); letter-spacing:1px; margin:16px 0 8px;
                border-right:3px solid #6be0c8; padding-right:10px;">
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
        ws   = status_with_icon(wt, ww, wh)
        st.markdown(render_current_weather(
            location_name, wt, wh, ww, wwd, wdesc, ws,
            is_base=bool(clicked_base), lat=clat, lon=clon
        ), unsafe_allow_html=True)
        daily, fc_source = get_daily_forecast(clat, clon)
        if daily:
            tab_cards3, tab_chart3 = st.tabs(["🗂️ כרטיסים", "📈 גרף"])
            with tab_cards3:
                st.markdown(render_forecast(daily), unsafe_allow_html=True)
            with tab_chart3:
                st.altair_chart(build_forecast_chart(daily), use_container_width=True)
                st.altair_chart(build_humidity_wind_chart(daily), use_container_width=True)
            st.caption(forecast_source_caption(fc_source, len(daily)))
            excel_bytes = create_forecast_excel(location_name, clat, clon, daily)
            st.download_button(
                label="📥 ייצוא תחזית ל-Excel",
                data=excel_bytes,
                file_name=f"forecast_{location_name.replace(',','_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_map_click"
            )

st.markdown("<hr style='border-color:rgba(107,224,200,0.1); margin:20px 0;'>", unsafe_allow_html=True)

# ================== BASE TABLE ==================
if st.session_state.bases:
    header_col, pdf_col = st.columns([3, 1])
    with header_col:
        st.markdown("""
        <div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
                    color:rgba(107,224,200,0.6); letter-spacing:1px; margin-bottom:14px;
                    border-right:3px solid #6be0c8; padding-right:10px;">
            ◉ בסיסים פעילים — מצב מזג אוויר
        </div>
        """, unsafe_allow_html=True)
    with pdf_col:
        pdf_bytes = generate_pdf_report(st.session_state.bases)
        st.download_button(
            label="📄 דוח PDF מרוכז",
            data=pdf_bytes,
            file_name=f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_pdf_report"
        )

    # ── Filter / sort / favorites controls ──
    f1, f2, f3, f4 = st.columns([1.2, 1.2, 1, 1])
    with f1:
        status_filter = st.selectbox("סנן לפי סטטוס", ["הכל", "תקין", "בינוני", "מסוכן"], key="status_filter")
    with f2:
        sort_by = st.selectbox("מיין לפי", ["שם", "טמפ׳ (גבוה→נמוך)", "סטטוס (חמור→קל)"], key="sort_by")
    with f3:
        fav_only = st.checkbox("⭐ מועדפים בלבד", key="fav_only")
    with f4:
        if st.button("🔄 רענן הכל", use_container_width=True, key="refresh_all_btn"):
            st.session_state.new_alerts = refresh_all_bases()
            st.rerun()

    display_bases = list(st.session_state.bases)
    if status_filter != "הכל":
        display_bases = [b for b in display_bases if strip_status_icon(b.get("status", "")) == status_filter]
    if fav_only:
        display_bases = [b for b in display_bases if b.get("favorite")]

    severity_rank = {"מסוכן": 0, "בינוני": 1, "תקין": 2}
    if sort_by == "שם":
        display_bases.sort(key=lambda b: b["name"])
    elif sort_by == "טמפ׳ (גבוה→נמוך)":
        display_bases.sort(key=lambda b: b.get("temp", -999), reverse=True)
    else:
        display_bases.sort(key=lambda b: severity_rank.get(strip_status_icon(b.get("status", "")), 3))
    display_bases.sort(key=lambda b: not b.get("favorite", False))  # favorites float to top

    if not display_bases:
        st.info("אין בסיסים התואמים את הסינון שנבחר")

    cols = st.columns(min(len(display_bases), 3)) if display_bases else []
    for i, b in enumerate(display_bases):
        sc = status_color_hex(b.get("status", "תקין"))
        star = "⭐" if b.get("favorite") else "☆"
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.45); border:1px solid {sc}33;
                        border-top:3px solid {sc}; border-radius:8px; padding:16px;
                        margin-bottom:8px; direction:rtl; transition: all 0.2s;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="font-family:'Heebo',sans-serif; font-size:16px; font-weight:700; color:{sc};">
                        {b['name']}
                    </div>
                    <div style="font-size:15px;">{star}</div>
                </div>
                <div style="font-family:'Heebo',sans-serif; font-size:13px;
                            line-height:2.0; color:rgba(232,236,245,0.85);">
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

            # ── Favorite / Forecast / History buttons ──
            btn_col0, btn_col1, btn_col2 = st.columns(3)
            with btn_col0:
                if st.button("⭐" if not b.get("favorite") else "★", key=f"fav_{b['name']}", use_container_width=True):
                    b["favorite"] = not b.get("favorite", False)
                    save_bases(st.session_state.bases)
                    st.rerun()
            with btn_col1:
                if st.button("📅 תחזית", key=f"fc_{b['name']}", use_container_width=True):
                    show_forecast_dialog(b)
            with btn_col2:
                if st.button("📈 היסטוריה", key=f"hist_{b['name']}", use_container_width=True):
                    st.session_state.history_base = (
                        None if st.session_state.history_base == b["name"] else b["name"]
                    )
                    st.rerun()

            # ── History / trend chart, toggled per base ──
            if st.session_state.history_base == b["name"]:
                hist = [r for r in load_history() if r["base"] == b["name"]]
                if len(hist) < 2:
                    st.info("עדיין אין מספיק היסטוריה שמורה לבסיס זה — היא נאספת אוטומטית בכל רענון (בטעינת האפליקציה או בכפתור '🔄 רענן הכל').")
                else:
                    df = pd.DataFrame(hist)
                    df["ts"] = pd.to_datetime(df["ts"])
                    df = df.set_index("ts")[["temp", "hum", "wind"]]
                    df.columns = ["טמפרטורה (°C)", "לחות (%)", "רוח (מ/ש)"]
                    st.line_chart(df)

# ================== ADMIN PANEL ==================
if is_admin:
    st.markdown("""
    <div style="background:rgba(107,224,200,0.03); border:1px solid rgba(107,224,200,0.2);
                border-radius:10px; padding:24px; margin-top:24px;">
        <div style="font-family:'Heebo',sans-serif; font-size:18px; font-weight:700;
                    color:#6be0c8; letter-spacing:2px; margin-bottom:18px; text-align:center;
                    border-bottom:1px solid rgba(107,224,200,0.15); padding-bottom:12px;">
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
                        color:rgba(107,224,200,0.6); margin-bottom:12px; direction:rtl;">
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
                        s  = status_with_icon(t, wd, h)
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

            st.markdown("""
            <div style="font-family:'Heebo',sans-serif; font-size:12px; color:rgba(107,224,200,0.6);
                        margin:14px 0 6px; direction:rtl;">
                ⚙️ ספי התראה מותאמים אישית לבסיס זה (משפיעים על מתי הבסיס ייחשב "מסוכן")
            </div>
            """, unsafe_allow_html=True)
            th_col1, th_col2, th_col3 = st.columns(3)
            with th_col1:
                new_th_temp = st.number_input("סף טמפ׳ (°C)", value=float(base.get("th_temp", DEFAULT_TH_TEMP)), key="edit_th_temp")
            with th_col2:
                new_th_wind = st.number_input("סף רוח (מ/ש)", value=float(base.get("th_wind", DEFAULT_TH_WIND)), key="edit_th_wind")
            with th_col3:
                new_th_hum = st.number_input("סף לחות (%)", value=float(base.get("th_hum", DEFAULT_TH_HUM)), key="edit_th_hum")

            if st.button("💾 שמור שינויים", use_container_width=True):
                base["name"]    = new_name
                base["th_temp"] = new_th_temp
                base["th_wind"] = new_th_wind
                base["th_hum"]  = new_th_hum
                save_bases(st.session_state.bases)
                st.success("✅ השינויים נשמרו")
                st.rerun()
        else:
            st.info("אין בסיסים לעריכה")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Recent alerts log ──
    recent = list(reversed(load_alerts()[-20:]))
    if recent:
        st.markdown("""
        <div style="font-family:'Heebo',sans-serif; font-size:14px; font-weight:700;
                    color:#ff5f6b; letter-spacing:1px; margin:20px 0 10px; direction:rtl;">
            🚨 יומן התראות אחרונות
        </div>
        """, unsafe_allow_html=True)
        rows = "".join(
            f"<div style='font-family:Heebo,sans-serif; font-size:12px; color:rgba(232,236,245,0.75); "
            f"padding:6px 0; border-bottom:1px solid rgba(255,95,107,0.12); direction:rtl;'>"
            f"{a['ts']} &nbsp;·&nbsp; <b style='color:#ff5f6b;'>{a['base']}</b> &nbsp;"
            f"{a['from']} ← {a['to']}</div>"
            for a in recent
        )
        st.markdown(f"<div>{rows}</div>", unsafe_allow_html=True)
        smtp_configured = False
        try:
            smtp_configured = "smtp" in st.secrets
        except Exception:
            smtp_configured = False
        if not smtp_configured:
            st.caption("💡 התראות מייל אינן מוגדרות. הוסיפי מקטע [smtp] ל-st.secrets (host/port/user/password/from_addr/to_addr) כדי להפעיל שליחה אוטומטית.")

# ── Footer ──
st.markdown("""
<div style="text-align:center; padding:30px 0 10px; font-family:'Heebo',sans-serif;
            font-size:11px; color:rgba(107,224,200,0.2); letter-spacing:2px; direction:rtl;">
    חמל שמי שליטה · סווג · כל הזכויות שמורות · HAMAL SKY CONTROL · CLASSIFIED
</div>
""", unsafe_allow_html=True)
