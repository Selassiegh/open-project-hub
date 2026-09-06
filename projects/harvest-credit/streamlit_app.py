import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/api")
LANGUAGES = {"English": "en", "Afrikaans": "af", "isiZulu": "zu"}
COPY = {
    "en": {"title": "Harvest Credit", "subtitle": "Simple harvest-time credit for your cooperative", "owed": "What farmers owe", "kyc": "KYC waiting", "lines": "Active credit", "payouts": "Weather payouts", "farmer": "Farmer phone", "pin": "Co-op PIN", "login": "Open farmer view", "refresh": "Refresh dashboard", "packages": "Input packages"},
    "af": {"title": "Harvest Credit", "subtitle": "Eenvoudige krediet vir jou koöperasie", "owed": "Wat boere skuld", "kyc": "KYC wag", "lines": "Aktiewe krediet", "payouts": "Weeruitbetalings", "farmer": "Boer se foon", "pin": "Koöperasie-PIN", "login": "Maak boer-aansig oop", "refresh": "Verfris paneel", "packages": "Insetpakkette"},
    "zu": {"title": "Harvest Credit", "subtitle": "Isikweletu esilula somfelandawonye", "owed": "Lokho abalimi abakweletayo", "kyc": "I-KYC elindile", "lines": "Isikweletu esisebenzayo", "payouts": "Izinkokhelo zesimo sezulu", "farmer": "Ucingo lomlimi", "pin": "I-PIN yomfelandawonye", "login": "Vula ukubuka komlimi", "refresh": "Vuselela iphaneli", "packages": "Amaphakheji okufaka"},
}


def api_get(path: str):
    response = requests.get(f"{API_URL}{path}", timeout=5)
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="Harvest Credit", page_icon="🌾", layout="centered")
language = st.sidebar.selectbox("Language / Taal / Ulimi", list(LANGUAGES))
text = COPY[LANGUAGES[language]]
st.title(f"🌾 {text['title']}")
st.caption(text["subtitle"])

try:
    dashboard = api_get("/dashboard")
    columns = st.columns(4)
    for column, icon, label, key in zip(columns, ["🧾", "⏳", "💳", "☔"], [text["owed"], text["kyc"], text["lines"], text["payouts"]], ["total_owed_zar", "pending_kyc", "active_credit_lines", "triggered_payouts"]):
        value = dashboard.get(key, 0)
        column.metric(f"{icon} {label}", f"ZAR {float(value):,.2f}" if key == "total_owed_zar" else value)
except requests.RequestException:
    st.error("The Harvest Credit API is not running. Start it with uvicorn first.")
    st.stop()

if st.button(f"🔄 {text['refresh']}", use_container_width=True):
    st.rerun()

st.divider()
st.subheader(f"📱 {text['login']}")
with st.form("farmer-login"):
    phone = st.text_input(text["farmer"], value="+27820000001")
    pin = st.text_input(text["pin"], value="1234", type="password")
    submitted = st.form_submit_button(f"✅ {text['login']}", use_container_width=True)
if submitted:
    response = requests.post(f"{API_URL}/auth/login", json={"phone": phone, "pin": pin}, timeout=5)
    if response.ok:
        farmer = response.json()
        st.success(f"{farmer['name']} • {api_get(f'/farmers/{farmer["farmer_id"]}/sms-summary')['message']}")
    else:
        st.error("Please check the phone number and PIN.")

st.divider()
st.subheader(f"📦 {text['packages']}")
for package in api_get("/input-packages"):
    st.button(f"🌱 {package['name']} · ZAR {float(package['cost_zar']):,.2f}", key=f"package-{package['id']}", use_container_width=True)
