import json
from datetime import date, timedelta

import requests
import streamlit as st

API = "https://yarta-planner-mx6jechunkpbjpbpzefhkt.streamlit.app/"
CURRENCIES = ["INR", "USD", "EUR", "GBP", "AED", "SGD", "THB", "JPY", "AUD", "CAD"]

st.set_page_config(page_title="Yatra Planner", page_icon="🧭", layout="centered")

st.markdown(
    """
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 3rem; max-width: 820px;}
html, body, [class*="css"] {font-family: 'Inter', system-ui, sans-serif;}
h1 {font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0;}
.sub {opacity: .6; margin-bottom: 1.6rem;}
.sec {font-size: .78rem; text-transform: uppercase; letter-spacing: .12em;
      opacity: .55; margin: 2.2rem 0 .8rem;}
.card {border: 1px solid rgba(128,128,128,.25); border-radius: 14px;
       padding: 14px 16px; margin-bottom: 12px;}
.card p {margin: 6px 0 0; opacity: .85; font-size: .92rem;}
.big {font-size: 1.6rem; font-weight: 600; line-height: 1.2;}
.muted {opacity: .6; font-size: .85rem;}
.row {display: flex; justify-content: space-between; align-items: center;}
.pill {font-size: .72rem; padding: 2px 10px; border-radius: 999px;
       border: 1px solid rgba(128,128,128,.35); opacity: .8;}
div.stButton > button {border-radius: 10px; width: 100%; height: 2.8rem;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("# 🧭 Yatra Planner")
st.markdown("<div class='sub'>Weather, places and currency in one plan.</div>", unsafe_allow_html=True)


# ---------- renderers ----------
def section(title):
    st.markdown(f"<div class='sec'>{title}</div>", unsafe_allow_html=True)


def render_weather(items):
    section("Weather")
    for i in range(0, len(items), 4):
        cols = st.columns(4)
        for col, w in zip(cols, items[i : i + 4]):
            d = w.get("date")
            label = date.fromisoformat(d).strftime("%a, %d %b") if d else w.get("destination", "").title()
            col.markdown(
                f"""<div class='card'>
                <div class='muted'>{label}</div>
                <div class='big'>{round(w['temperature_high'])}° <span class='muted'>/ {round(w['temperature_low'])}°</span></div>
                <div>{w['condition']}</div>
                <div class='muted'>💧 {round(w['humidity'])}% · 🌧 {round(w['rain_chance'])}%</div>
                </div>""",
                unsafe_allow_html=True,
            )


def render_places(items):
    section("Places")
    for p in sorted(items, key=lambda x: x.get("rating", 0), reverse=True):
        fee = p.get("entry_fee")
        fee_txt = "—" if fee is None else ("Free" if fee == 0 else f"{fee:g}")
        st.markdown(
            f"""<div class='card'>
            <div class='row'><b>{p['name']}</b><span class='pill'>{p['category']}</span></div>
            <div class='muted'>★ {p['rating']:.1f} · {p['estimated_time_hours']:g} h · Entry: {fee_txt}</div>
            <p>{p['description']}</p></div>""",
            unsafe_allow_html=True,
        )


def render_currency(rates, base, budget):
    section("Currency")
    default = [c for c in CURRENCIES if c in rates and c != base][:4]
    picks = st.multiselect("Convert budget to", sorted(rates), default=default, key="picks")
    st.caption(f"Budget: {budget:,.0f} {base}")
    base_rate = rates.get(base, 1)
    for i in range(0, len(picks), 4):
        cols = st.columns(4)
        for col, c in zip(cols, picks[i : i + 4]):
            col.metric(c, f"{budget * rates[c] / base_rate:,.2f}")


def render_all(r):
    if r.get("title"):
        st.markdown(f"### {r['title']}")
    if r.get("weather"):
        render_weather(r["weather"])
    if r.get("places"):
        render_places(r["places"])
    if r.get("currency"):
        render_currency(r["currency"], r["base"], r["budget"])


# ---------- api ----------
def fetch_plan(payload):
    r = requests.post(f"{API}/plan/", json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(r.json().get("detail", r.text))
    d = r.json()
    return {
        "weather": d["weather_data"],
        "places": d["places_data"],
        "currency": d["currency_rate"],
    }


def stream_plan(payload, on_event):
    with requests.post(f"{API}/stream/plan", json=payload, stream=True, timeout=120) as r:
        if r.status_code != 200:
            raise RuntimeError(r.json().get("detail", r.text))
        r.encoding = "utf-8"
        event = None
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                on_event(event, json.loads(line[5:].strip()))


# ---------- form ----------
c1, c2 = st.columns([2, 1])
dest = c1.text_input("Destination", placeholder="e.g. Goa")
base = c2.selectbox("Currency", CURRENCIES)

c3, c4, c5 = st.columns(3)
start = c3.date_input("From", date.today() + timedelta(days=1))
end = c4.date_input("To", date.today() + timedelta(days=4))
budget = c5.number_input("Budget", min_value=0.0, value=20000.0, step=1000.0)

live = st.toggle("Live stream", value=True)
go = st.button("Plan my trip", type="primary")

# ---------- run ----------
if go:
    if not dest.strip():
        st.warning("Enter a destination.")
    elif start > end:
        st.warning("Start date can't be after end date.")
    else:
        payload = {
            "destination": dest.strip(),
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "base_currency": base,
        }
        title = f"{dest.strip().title()} · {start:%d %b} – {end:%d %b}"
        result = {"base": base, "budget": budget, "title": title}
        try:
            if live:
                st.markdown(f"### {title}")
                status = st.empty()
                w_ph, p_ph, c_ph = st.empty(), st.empty(), st.empty()

                def handle(event, data):
                    if "message" in data:
                        status.caption(data["message"])
                    if event == "weathe_complete":
                        result["weather"] = data["weather_data"]
                        with w_ph.container():
                            render_weather(result["weather"])
                    elif event == "Options_complete":
                        result["places"] = data["places_data"]
                        with p_ph.container():
                            render_places(result["places"])
                    elif event == "currency_complete":
                        result["currency"] = data["currency_data"]
                        with c_ph.container():
                            render_currency(result["currency"], base, budget)
                    elif event == "complete":
                        status.empty()

                stream_plan(payload, handle)
                st.session_state.result = result
            else:
                with st.spinner("Planning..."):
                    result.update(fetch_plan(payload))
                st.session_state.result = result
                render_all(result)
        except requests.exceptions.ConnectionError:
            st.error("Can't reach the API. Is FastAPI running?")
        except Exception as e:
            st.error(str(e))
elif "result" in st.session_state:
    render_all(st.session_state.result)