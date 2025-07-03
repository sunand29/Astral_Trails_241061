# cosmic_ray_explorer.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px  # ✅ Replaces matplotlib

st.set_page_config(page_title="Cosmic Ray Data Explorer", layout="wide")

st.title("☄️ Cosmic Ray Data Explorer")
st.markdown("""
Visualize **cosmic ray flux vs. energy** using real data from the [Cosmic Ray Database (CRDB)](https://lpsc.in2p3.fr/crdb/).
""")

# --- Dropdowns
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
log_scale = st.checkbox("📉 Use Log Scale", value=True)

# --- Button
if st.button("📡 Fetch and Plot Cosmic Ray Data"):
    st.info("Fetching data from CRDB API...")

    query_url = f"https://lpsc.in2p3.fr/crdb/api_v1/dataset?exp={source}&nuc={particle_code[particle]}"

    try:
        response = requests.get(query_url)
        data = response.json()

        if not data or 'datasets' not in data or len(data['datasets']) == 0:
            st.warning("No data found for this selection.")
        else:
            flux_data = []

            for dataset in data['datasets']:
                for point in dataset.get('data', []):
                    if point.get('e_kn') and point.get('val'):
                        flux_data.append({
                            'Energy (GeV/n)': point['e_kn'],
                            'Flux': point['val']
                        })

            df = pd.DataFrame(flux_data).dropna().sort_values(by='Energy (GeV/n)')

            if df.empty:
                st.error("No usable data points.")
            else:
                # --- Plotly Chart
                fig = px.line(df,
                              x="Energy (GeV/n)",
                              y="Flux",
                              title=f"{particle} Flux from {source}",
                              markers=True,
                              log_x=True if log_scale else False,
                              log_y=True if log_scale else False)
                fig.update_layout(xaxis_title="Energy (GeV/nucleon)",
                                  yaxis_title="Flux [particles/m²·sr·s·GeV/n]",
                                  template="plotly_dark")

                st.plotly_chart(fig, use_container_width=True)

                st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=f"{source}_{particle_code[particle]}_flux.csv")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
