import streamlit as st
import geopandas as gpd
import pandas as pd
import leafmap.foliumap as leafmap
import matplotlib.pyplot as plt

# Set Streamlit page config to wide mode
st.set_page_config(layout="wide")

# Cache data loading for performance
@st.cache_data
def load_data():
    Data = gpd.read_file("Data\Data.shp").to_crs("EPSG:4326")

    # Convert population columns to numeric
    pop_cols = [col for col in Data.columns if col.isdigit()]
    Data[pop_cols] = Data[pop_cols].replace(',', '', regex=True).astype(float)

    return Data

# Load the data
Data = load_data()

# Extract columns with years (population data)
pop_cols = [col for col in Data.columns if col.isdigit()]

# Streamlit title 
st.markdown("<h1 style='text-align: center;'>Right Section: Graph and Growth Analysis</h1>", unsafe_allow_html=True)

# Layout: left for controls and map, right for graph
left, right = st.columns([2.9, 3])

# Left section: Borough selection and map display
with left:
    borough_names = Data["NAME"].unique().tolist()  # replace with actual name column if different
    selected_borough = st.selectbox("Select a Borough", ["None"] + borough_names)

    # Map
    m = leafmap.Map(center=[51.5074, -0.1278], zoom=10, zoom_control=False, dragging=False)

    # Base style before selection
    base_style = {
        "fillColor": "#ADD8E6",
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.5
    }

    # Highlight style for selected borough
    highlight_style = {
        "fillColor": "#003366",
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.9
    }

    # Add all boroughs to the map
    m.add_gdf(Data, layer_name="All Boroughs", style=base_style, info_mode=None)

    # Highlight selected borough if one is chosen
    if selected_borough != "None":
        selected = Data[Data["NAME"] == selected_borough]
        m.add_gdf(selected, layer_name="Selected Borough", style=highlight_style, info_mode=None, zoom_to_layer=False)

    m.to_streamlit(height=550)

# Right section: Graph and growth analysis
with right:
    if selected_borough != "None":
        st.markdown(f"<h3 style='padding-left: 20px;'>Population of {selected_borough} (1801–2021)</h3>", unsafe_allow_html=True)
        selected_row = Data[Data["NAME"] == selected_borough]

        if not selected_row.empty:
            # Extract population values
            pop_values = selected_row[pop_cols].values.flatten()

            # Line Chart
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(pop_cols, pop_values, marker='o', linestyle='-', color='navy')
            ax.set_xlabel("Year")
            ax.set_ylabel("Population")
            ax.set_title(f"Population growth 1801–2021: {selected_borough}")
            ax.grid(True)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Population for selected year
            year_lookup = st.selectbox("Select a year to view population", pop_cols, index=len(pop_cols) - 1, key="borough_lookup_year")
            population_lookup = selected_row[year_lookup].values[0]

            st.markdown(
                f"<h4>Population in {year_lookup}: <span style='color:#1f77b4;'>{int(population_lookup):,}</span></h4>",
                unsafe_allow_html=True
            )

            # Year selection and growth %
            col1, col2 = st.columns(2)
            with col1:
                year_start = st.selectbox("Start Year", pop_cols, index=0)
            with col2:
                year_end = st.selectbox("End Year", pop_cols, index=len(pop_cols) - 1)

            try:
                # Extract values for selected years
                pop_start = selected_row[year_start].values[0]
                pop_end = selected_row[year_end].values[0]

                if pd.notna(pop_start) and pd.notna(pop_end) and pop_start != 0:
                    growth = ((pop_end - pop_start) / pop_start) * 100
                    st.markdown(
                        f"<h4 style='padding-top: 30px;'>Population Growth ({year_start}–{year_end}): "
                        f"<span style='color:green;'>{growth:.2f}%</span></h4>",
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Population values are missing or zero.")
            except Exception as e:
                st.warning(f"Could not calculate growth. Error: {e}")
        else:
            st.warning("Population data not found for this borough.")
    
    else:
        # Display total Greater London population chart if no borough selected
        st.markdown("<h3 style='padding-left: 30px;'>Population Growth Greater London (1801–2021)</h3>", unsafe_allow_html=True)

        if len(pop_cols) > 0:
            total_pop = Data[pop_cols].sum()

            # Plot total population trend
            fig, ax = plt.subplots(figsize=(15, 5))
            ax.plot(pop_cols, total_pop, marker='o', linestyle='-', color='darkgreen')
            ax.set_xlabel("Year")
            ax.set_ylabel("Total Population")
            ax.set_title("Population Trend: Greater London")
            ax.grid(True)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Population for selected year
            year_lookup = st.selectbox("Select a year to view total population", pop_cols, index=len(pop_cols) - 1, key="total_lookup_year")
            population_lookup = Data[year_lookup].sum()

            st.markdown(
                f"<h4>Total Population in {year_lookup}: <span style='color:#1f77b4;'>{int(population_lookup):,}</span></h4>",
                unsafe_allow_html=True
            )

            # percentage of population growth
            col1, col2 = st.columns(2)
            with col1:
                year_start = st.selectbox("Start Year", pop_cols, index=0, key="total_start")
            with col2:
                year_end = st.selectbox("End Year", pop_cols, index=len(pop_cols) - 1, key="total_end")

            try:
                pop_start = Data[year_start].sum()
                pop_end = Data[year_end].sum()

                if pop_start != 0:
                    growth = ((pop_end - pop_start) / pop_start) * 100
                    st.markdown(
                        f"<h4 style='padding-top: 10px;'>Population Growth ({year_start}–{year_end}): "
                        f"<span style='color:green;'>{growth:.2f}%</span></h4>",
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Start year population is zero.")
            except Exception as e:
                st.warning(f"Could not calculate growth. Error: {e}")
