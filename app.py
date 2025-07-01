import streamlit as st
import requests
import pandas as pd

# # --- Page Config ---
# st.set_page_config(page_title="Radiation Risk Dashboard", layout="wide")
# st.title("🚀 Cosmic Radiation Risk Dashboard")

# # --- Real-time Proton Flux from NOAA ---
# try:
#     proton_url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"
#     proton_data = requests.get(proton_url).json()
#     flux = float(proton_data[-1]['flux'])
#     st.toast("Proton flux fetched successfully!", icon="✅")
# except:
#     flux = 100
#     st.warning("Could not fetch live proton flux. Using fallback value: 100 p/cm²/s/sr")

# # --- Real-time Kp Index from NOAA ---
# try:
#     kp_url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
#     kp_raw = requests.get(kp_url).json()
#     kp_df = pd.DataFrame(kp_raw[1:], columns=["time_tag", "kp"])
#     kp_df["time_tag"] = pd.to_datetime(kp_df["time_tag"])
#     kp_df["kp"] = kp_df["kp"].astype(float)
#     latest_kp = kp_df["kp"].iloc[-1]
# except:
#     latest_kp = None
#     st.warning("Could not retrieve Kp index data.")

# # --- Solar Alerts ---
# try:
#     alerts_url = "https://services.swpc.noaa.gov/products/alerts.json"
#     alerts = requests.get(alerts_url).json()
#     recent_alerts = alerts[-5:]
# except:
#     recent_alerts = []
#     st.warning("Could not fetch SWPC solar alerts.")

# # --- Dashboard Metrics ---
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric("☀ Proton Flux (≥10 MeV)", f"{flux:.2e} p/cm²/s/sr")
# with col2:
#     if latest_kp is not None:
#         st.metric("🧲 Kp Index", f"{latest_kp:.2f}")
#     else:
#         st.metric("🧲 Kp Index", "--")
# with col3:
#     st.markdown("### 🔔 Recent SWPC Alerts")
#     for a in recent_alerts:
#         time = a.get('issue_time', 'No time')
#         msg = a.get('message', 'No message available')
#         st.caption(f"{time} — {msg}")

# # --- Proton Flux Chart ---
# try:
#     df = pd.DataFrame(proton_data)
#     df['time_tag'] = pd.to_datetime(df['time_tag'])
#     df['flux'] = df['flux'].astype(float)
#     st.line_chart(df.set_index('time_tag')['flux'])
# except:
#     pass

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Risk Assessment", "🧬 Biology Impact", "✈️ Flight Dose"])

with tab1:
    st.header("📊 Radiation Risk Calculator")
    mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
    shielding_material = st.selectbox("Shielding Material", ["None", "Aluminum", "Polyethylene"])
    base_dose_per_day = flux * 0.00005
    shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
    daily_dose = base_dose_per_day * shield_factors[shielding_material]
    total_dose = daily_dose * mission_days
    risk_percent = (total_dose / 1000) * 5
    st.success(f"☢ Estimated Total Dose: {total_dose:.2f} mSv")
    st.info(f"⚠ Estimated Cancer Risk: {risk_percent:.2f} %")

with tab2:
    st.header("🧬 DNA Damage Estimator")
    cell_type = st.selectbox("Target Cell Type", ["Skin Cell", "Neuron", "Lymphocyte", "Germ Cell"])
    dsb_per_gy = {"Skin Cell": 1000, "Neuron": 800, "Lymphocyte": 1200, "Germ Cell": 1500}
    repair_eff = {"Skin Cell": 0.95, "Neuron": 0.8, "Lymphocyte": 0.9, "Germ Cell": 0.7}
    dsb = total_dose * dsb_per_gy[cell_type] / 1000
    repaired = dsb * repair_eff[cell_type]
    remaining = dsb - repaired
    st.write(f"Estimated DSBs: **{dsb:.0f}**, Repaired: **{repaired:.0f}**, Unrepaired: **{remaining:.0f}**")

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
    st.write(f"Adjusted Cancer Risk: **{organ_risk:.2f} %**")

with tab3:
    st.header("✈️ Flight Dose Estimator")
    flight = st.selectbox("Flight Path", ["Delhi to New York", "Tokyo to San Francisco", "Paris to Cape Town"])
    flight_hours = {"Delhi to New York": 15, "Tokyo to San Francisco": 11, "Paris to Cape Town": 12}
    alt_dose_per_hr = 0.005
    flight_dose = flight_hours[flight] * alt_dose_per_hr
    st.write(f"Estimated In-Flight Radiation Dose: **{flight_dose:.2f} mSv**")

    st.header("🌍 Altitude & Latitude Dose Variation")
    altitude_km = st.slider("Altitude (km)", 0, 20, 1)
    latitude = st.slider("Latitude (degrees)", 0, 90, 45)
    alt_factor = 2 ** (altitude_km / 2)
    lat_factor = 1 + (latitude / 90)
    adjusted_dose = total_dose * alt_factor * lat_factor
    st.write(f"Adjusted Dose: **{adjusted_dose:.2f} mSv**")

st.caption("Note: This tool is for educational and research purposes only. Data powered by NOAA SWPC & ICRP models.")
