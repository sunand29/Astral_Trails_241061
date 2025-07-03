# cosmic_ray_explorer.py

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Cosmic Ray Data Explorer", layout="wide")

st.title("☄️ Cosmic Ray Data Explorer")
st.markdown("""
This app visualizes **cosmic ray flux vs. energy** using real data from the [Cosmic Ray Database (CRDB)](https://lpsc.in2p3.fr/crdb).
""")

# --- Selection Controls ---
sources = ['Voyager', 'AMS-02', 'ACE', 'PAMELA', 'SOHO']
particles = ['Proton (H)', 'Helium (He)', 'Carbon (C)', 'Electron (e−)']
particle_code = {
    'Proton (H)': 'H',
    'Helium (He)': 'He',
    'Carbon (C)': 'C',
    'Electron (e−)': 'e'
}

source = st.selectbox("🔭 Choose Cosmic Ray Source", sources)
particle = st.selectbox("🧪 Choose Particle Type", particles)
log_scale = st.checkbox("📉 Use Log Scale for Y-axis (Flux)", value=True)

# --- Fetch & Plot Data ---
if st.button("📡 Fetch and Plot Cosmic Ray Data"):
    st.info("Querying CRDB... Please wait.")
    
    api_url = f"https://lpsc.in2p3.fr/crdb/api_v1/dataset?exp={source}&nuc={particle_code[particle]}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if not data or 'datasets' not in data or len(data['datasets']) == 0:
            st.warning("No datasets found for this selection.")
        else:
            flux_data = []

            for dataset in data['datasets']:
                for point in dataset.get('data', []):
                    flux_data.append({
                        'Energy (GeV/n)': point.get('e_kn'),
                        'Flux': point.get('val')
                    })

            df = pd.DataFrame(flux_data).dropna()
            df = df.sort_values('Energy (GeV/n)')

            if df.empty:
                st.error("No valid flux data available.")
            else:
                # Plot using matplotlib
                fig, ax = plt.subplots()
                ax.plot(df['Energy (GeV/n)'], df['Flux'], marker='o', linestyle='-')
                ax.set_xlabel("Energy [GeV/nucleon]")
                ax.set_ylabel("Flux [particles/(m²·sr·s·GeV/n)]")
                ax.set_title(f"{particle} Flux from {source}")

                if log_scale:
                    ax.set_yscale('log')
                    ax.set_xscale('log')

                ax.grid(True, which='both', linestyle='--', alpha=0.5)
                st.pyplot(fig)

                with st.expander("📄 View Raw Data"):
                    st.dataframe(df)

                st.download_button("⬇️ Download CSV", data=df.to_csv(index=False), file_name=f"{source}_{particle_code[particle]}_flux.csv", mime="text/csv")
    
    except Exception as e:
        st.error(f"Failed to retrieve data: {e}")
