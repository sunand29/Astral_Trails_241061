import streamlit as st
import requests
import pandas as pd

# Page setup
st.set_page_config(page_title="Radiation Risk Calculator", layout="centered")
st.title("Cosmic Radiation Risk Calculator")

# --- User Inputs ---
mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
shielding_material = st.selectbox("Shielding Material", ["None", "Aluminum", "Polyethylene"])

# --- Real-time proton flux from NOAA ---
url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"
try:
    data = requests.get(url).json()
    flux = float(data[-1]['flux'])
    st.success(f"Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")
except:
    flux = 100
    st.warning("Unable to fetch live data. Using default flux: 100 p/cm²/s/sr")

# --- Base Dose Calculation ---
base_dose_per_day = flux * 0.00005
shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
daily_dose = base_dose_per_day * shield_factors[shielding_material]
total_dose = daily_dose * mission_days
risk_percent = (total_dose / 1000) * 5

st.metric("☢ Estimated Total Dose (mSv)", f"{total_dose:.2f}")
st.metric("⚠ Estimated Cancer Risk", f"{risk_percent:.2f} %")

# --- DNA Damage Estimator ---
st.header("🧬 DNA Damage Estimator")
cell_type = st.selectbox("Target Cell Type", ["Skin Cell", "Neuron", "Lymphocyte", "Germ Cell"])
dsb_per_gy = {"Skin Cell": 1000, "Neuron": 800, "Lymphocyte": 1200, "Germ Cell": 1500}
repair_eff = {"Skin Cell": 0.95, "Neuron": 0.8, "Lymphocyte": 0.9, "Germ Cell": 0.7}
dsb = total_dose * dsb_per_gy[cell_type] / 1000
repaired = dsb * repair_eff[cell_type]
remaining = dsb - repaired
st.write(f"Estimated DSBs: **{dsb:.0f}**, Repaired: **{repaired:.0f}**, Unrepaired: **{remaining:.0f}**")

# --- Altitude and Latitude Adjustment ---
st.header("🌍 Altitude & Latitude Dose Variation")
altitude_km = st.slider("Altitude (km)", 0, 20, 1)
latitude = st.slider("Latitude (degrees)", 0, 90, 45)
alt_factor = 2 ** (altitude_km / 2)
lat_factor = 1 + (latitude / 90)
adjusted_dose = total_dose * alt_factor * lat_factor
st.write(f"Adjusted Dose: **{adjusted_dose:.2f} mSv**")

# --- Age, Sex, Organ Risk ---
st.header("🚻 Age, Sex, and Organ-Specific Risk")
age = st.selectbox("Age Group", ["Child", "Young Adult", "Middle-aged", "Senior"])
sex = st.radio("Sex", ["Male", "Female"])
organ = st.selectbox("Organ", ["Whole Body", "Brain", "Lungs", "Gonads", "Bone Marrow"])
organ_weights = {"Whole Body": 1, "Brain": 0.05, "Lungs": 0.12, "Gonads": 0.20, "Bone Marrow": 0.12}
sex_factor = 1.2 if sex == "Female" else 1.0
age_factor = {"Child": 1.5, "Young Adult": 1.2, "Middle-aged": 1.0, "Senior": 0.8}[age]
effective_dose = total_dose * organ_weights[organ]
organ_risk = (effective_dose / 1000) * 5 * sex_factor * age_factor
st.write(f"Organ-weighted Effective Dose: **{effective_dose:.2f} mSv**")
st.write(f"Adjusted Risk: **{organ_risk:.2f} %**")

# --- Solar Proton Event Alert ---
st.header("☀️ Solar Proton Event Alert")
threshold = 10000
if flux > threshold:
    st.error("🚨 High Radiation Alert: Proton Event Detected!")
else:
    st.info("✅ Radiation levels within normal range.")

# --- Flight Path Dose Estimator ---
st.header("✈️ Flight Path Radiation Dose")
flight = st.selectbox("Flight Path", ["Delhi to New York", "Tokyo to San Francisco", "Paris to Cape Town"])
flight_hours = {"Delhi to New York": 15, "Tokyo to San Francisco": 11, "Paris to Cape Town": 12}
alt_dose_per_hr = 0.005
flight_dose = flight_hours[flight] * alt_dose_per_hr
st.write(f"Estimated In-Flight Radiation Dose: **{flight_dose:.2f} mSv**")

# --- Proton Flux Trend Chart ---
try:
    df = pd.DataFrame(data)
    df['time_tag'] = pd.to_datetime(df['time_tag'])
    df['flux'] = df['flux'].astype(float)
    st.line_chart(df.set_index('time_tag')['flux'])
except:
    pass

# --- Geomagnetic Kp Index ---
st.header("🧲 Geomagnetic Activity (Kp Index)")
kp_url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
try:
    kp_data = requests.get(kp_url).json()
    latest_kp = float(kp_data[-1]['k_index'])
    st.write(f"Current Geomagnetic Kp Index: **{latest_kp}**")
    if latest_kp >= 5:
        st.warning("⚠️ Geomagnetic Storm Level Detected (Kp ≥ 5)")
except:
    st.warning("Could not retrieve Kp index data.")

# --- SWPC Solar Event Alerts ---
st.header("🔔 SWPC Solar Event Alerts")
alerts_url = "https://services.swpc.noaa.gov/products/alerts.json"
try:
    alerts = requests.get(alerts_url).json()
    for alert in alerts[-5:]:
        st.markdown(f"**{alert['issue_time']}** — {alert['message']}")
except:
    st.warning("Could not fetch SWPC alerts.")

st.caption("Note: This tool is for educational and research purposes only. Based on ICRP guidelines and simplified models.")
