import streamlit as st
import requests
import pandas as pd

import socket
socket.gethostbyname("services.swpc.noaa.gov")

# --- Real-time Proton Flux from NOAA ---
proton_url = "https://services.swpc.noaa.gov/json/goes/primary/differential-electrons-1-day.json"
try:
    proton_data = requests.get(proton_url, timeout=10).json()
    
    # First row contains the column names
    headers = proton_data[0]  # ['time_tag', 'energy', 'flux', 'satellite', 'channel']
    rows = proton_data[1:]    # The actual data

    # Create a DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Filter for energy 10.0 MeV from GOES-18 satellite
    df = df[(df["energy"] == "10.0") & (df["satellite"] == "GOES-18")]
    
    # Convert flux column to numeric values
    df["flux"] = pd.to_numeric(df["flux"], errors="coerce")

    # Drop invalid flux values
    df.dropna(subset=["flux"], inplace=True)

    # Get the most recent flux value
    if not df.empty:
        flux = df["flux"].iloc[-1]
        st.toast("Proton flux fetched successfully!", icon="✅")
    else:
        flux = 100
        st.warning("No valid flux data available. Using fallback: 100")
except:
    flux = 100
    st.warning("Could not fetch live proton flux. Using fallback value: 100 p/cm²/s/sr")


tab1, tab2 = st.tabs(["📊 Risk Assessment", "🧬 Biology Impact"])

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
    
st.caption("Note: This tool is for educational and research purposes only. Data powered by NOAA SWPC & ICRP models.")
