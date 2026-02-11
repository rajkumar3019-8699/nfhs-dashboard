import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page Configuration
st.set_page_config(page_title="India NFHS Dashboard", layout="wide", page_icon="📊")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('NFHS_Cleaned.csv')
    # Identify data columns (excluding the first 3 identifier columns)
    indicators = df.columns[3:].tolist()
    return df, indicators

df, indicators = load_data()

# --- SIDEBAR ---
st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("Filter the data to explore specific regions and metrics.")

selected_survey = st.sidebar.selectbox("Select Survey Wave", options=df['Survey'].unique())
selected_area = st.sidebar.selectbox("Select Area Type", options=df['Area'].unique(), index=0)

# Filter global dataframe for comparisons
df_filtered = df[(df['Survey'] == selected_survey) & (df['Area'] == selected_area)]

selected_state = st.sidebar.selectbox("Select State/UT for Detail View", options=df_filtered['State/UT'].unique())
state_data = df_filtered[df_filtered['State/UT'] == selected_state].iloc[0]

# --- MAIN CONTENT ---
st.title(f"📊 India National Family Health Survey ({selected_survey})")
st.markdown(f"**Current View:** {selected_state} | **Area:** {selected_area}")

# --- KEY METRICS (KPIs) ---
st.markdown("### Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)

def get_val(col_name):
    val = state_data[col_name]
    return f"{val:.1f}" if not pd.isna(val) else "N/A"

with k1:
    st.metric("Female Literacy (%)", get_val("Women who are literate (%)"))
with k2:
    st.metric("Sex Ratio", get_val("Sex ratio of the total population (females per 1000 males)"))
with k3:
    st.metric("Infant Mortality Rate", get_val("Infant mortality rate (IMR)"))
with k4:
    st.metric("Institutional Births (%)", get_val("Institutional births (%)"))

st.divider()

# --- VISUALIZATIONS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("State-wise Comparison")
    selected_metric = st.selectbox("Select Metric to Compare", options=indicators, index=0)
    
    # Sort data for better visualization
    fig_bar = px.bar(
        df_filtered.sort_values(selected_metric, ascending=False),
        x='State/UT', y=selected_metric,
        color=selected_metric,
        color_continuous_scale='Viridis',
        title=f"{selected_metric} across India"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Urban vs Rural Gap")
    gap_metric = st.selectbox("Select Metric for Gap Analysis", options=indicators, index=10)
    
    gap_df = df[(df['Survey'] == selected_survey) & (df['State/UT'] == selected_state) & (df['Area'] != 'Total')]
    
    if not gap_df.empty:
        fig_gap = px.bar(
            gap_df, x='Area', y=gap_metric, color='Area',
            text_auto='.1f',
            title=f"Urban vs Rural: {gap_metric} in {selected_state}"
        )
        st.plotly_chart(fig_gap, use_container_width=True)
    else:
        st.info("Urban/Rural breakdown not available for this region.")

st.divider()

# --- CORRELATION ANALYSIS ---
st.subheader("Indicator Correlation Analysis")
c1, c2 = st.columns(2)
with c1:
    x_axis = st.selectbox("X-Axis Metric", options=indicators, index=11)
with c2:
    y_axis = st.selectbox("Y-Axis Metric", options=indicators, index=16)

fig_scatter = px.scatter(
    df_filtered, x=x_axis, y=y_axis, 
    hover_name='State/UT', trendline="ols",
    title=f"Correlation: {y_axis} vs {x_axis}"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- RAW DATA ---
with st.expander("View Cleaned Raw Data"):
    st.dataframe(df_filtered)
