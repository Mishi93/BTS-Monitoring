import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import random

st.set_page_config(page_title="BTS Monitoring Dashboard", layout="wide")

# -------------------------
# Load trained model
# -------------------------
model = joblib.load("bts_failure_model.pkl")

# -------------------------
# Page Header
# -------------------------
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>📡 Telecom BTS Monitoring Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------
# Sidebar Inputs
# -------------------------
st.sidebar.header("BTS Parameters")
location = st.sidebar.number_input("Location ID", 1, 100, 10)
event_count = st.sidebar.slider("Event Count", 0, 50, 10)
log_feature_count = st.sidebar.slider("Log Feature Count", 0, 50, 10)
resource_type_count = st.sidebar.slider("Resource Type Count", 0, 10, 3)
severity_type = st.sidebar.slider("Severity Type", 1, 5, 2)
volume = st.sidebar.slider("Log Volume", 0, 1000, 100)

input_data = pd.DataFrame({
    "location":[location],
    "event_type":[event_count],
    "log_feature":[log_feature_count],
    "resource_type":[resource_type_count],
    "severity_type":[severity_type],
    "volume":[volume]
})

# -------------------------
# Prediction Section
# -------------------------
st.subheader("🤖 BTS Failure Prediction")
prediction = None
prob = None

if st.button("Predict BTS Fault"):

    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0]

    st.markdown("### Input Data")
    st.dataframe(input_data)

    # Prediction result
    if prediction == 0:
        st.success("✅ BTS Operating Normally")
    elif prediction == 1:
        st.warning("⚠️ Minor Fault Detected")
    else:
        st.error("🚨 Major BTS Failure")

    # Probability Pie Chart
    prob_df = pd.DataFrame({
        "Fault Type":["No Fault","Minor Fault","Major Fault"],
        "Probability":prob
    })
    fig_prob = px.pie(
        prob_df,
        names="Fault Type",
        values="Probability",
        title="Fault Probability",
        color="Fault Type",
        color_discrete_map={"No Fault":"green","Minor Fault":"orange","Major Fault":"red"}
    )
    fig_prob.update_traces(textinfo='percent+label', pull=[0.05,0.05,0.1])
    st.plotly_chart(fig_prob, width='stretch')

    # Alarm Panel
    st.subheader("🚨 Network Alarm Panel")
    if prediction == 0:
        st.success("No active alarms")
    elif prediction == 1:
        st.warning("Minor network alarm triggered")
    else:
        st.error("Critical BTS alarm – Immediate action required")

st.markdown("---")

# -------------------------
# Activity & Trend Charts
# -------------------------
st.subheader("📈 BTS Activity & Fault Trend")

col1, col2 = st.columns(2)

with col1:
    # Activity Bar Chart
    metrics = pd.DataFrame({
        "Feature":["Events","Logs","Resources","Severity","Volume"],
        "Value":[event_count, log_feature_count, resource_type_count, severity_type, volume]
    })
    fig_bar = px.bar(
        metrics,
        x="Feature",
        y="Value",
        color="Feature",
        text="Value",
        title="BTS Activity Metrics",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, width="stretch")

with col2:
    # Fault Trend
    days = np.arange(1,31)
    faults = np.random.poisson(lam=prob[1]*5 if prob is not None else 3, size=30)
    trend_df = pd.DataFrame({"Day":days, "Faults":faults})
    fig_line = px.area(
        trend_df,
        x="Day",
        y="Faults",
        title="Monthly BTS Fault Trend",
        line_shape='spline',
        color_discrete_sequence=['#FF6F61']
    )
    fig_line.update_traces(mode='lines+markers', marker=dict(size=8))
    st.plotly_chart(fig_line, width="stretch")

st.markdown("---")

# -------------------------
# Network Load Gauge
# -------------------------
st.subheader("📡 Network Load Gauge")
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=volume,
    title={'text': "Network Load"},
    gauge={'axis': {'range': [0, 1000]},
           'bar': {'color': "#2E86C1"},
           'steps': [
               {'range': [0, 500], 'color': "#ABEBC6"},
               {'range': [500, 800], 'color': "#F9E79F"},
               {'range': [800, 1000], 'color': "#F5B7B1"}]}
))
st.plotly_chart(fig_gauge, width='stretch')

st.markdown("---")

# -------------------------
# BTS Map Visualization (Enhanced)
# -------------------------
st.subheader("🗺 BTS Network Risk Map")

location_coords = {
    i: (24.85 + random.uniform(-0.03, 0.03), 67.00 + random.uniform(-0.03, 0.03))
    for i in range(1, 101)
}
bts_map_data = pd.DataFrame([
    {"location": loc_id, "latitude": lat, "longitude": lon}
    for loc_id, (lat, lon) in location_coords.items()
])

# Fault probability
bts_map_data["fault_prob"] = np.random.uniform(0, 0.3, size=len(bts_map_data))
if prob is not None:
    bts_map_data.loc[bts_map_data["location"] == location, "fault_prob"] = prob[1]+prob[2]

# Status
def status_from_prob(p):
    if p < 0.1:
        return "Normal"
    elif p < 0.3:
        return "Minor Fault"
    else:
        return "Major Fault"
bts_map_data["status"] = bts_map_data["fault_prob"].apply(status_from_prob)

# Marker size
bts_map_data["size"] = 10 + bts_map_data["fault_prob"]*30
bts_map_data.loc[bts_map_data["location"] == location, "size"] += 10

# Map
fig_map = px.scatter_mapbox(
    bts_map_data,
    lat="latitude",
    lon="longitude",
    hover_name="location",
    hover_data=["status","fault_prob"],
    color="status",
    size="size",
    zoom=11,
    height=550,
    color_discrete_map={"Normal":"green","Minor Fault":"orange","Major Fault":"red"},
    opacity=0.7
)
fig_map.update_layout(
    mapbox_style="open-street-map",
    mapbox_center={"lat": bts_map_data["latitude"].mean(),
                   "lon": bts_map_data["longitude"].mean()},
    legend_title_text="BTS Status"
)
st.plotly_chart(fig_map, width='stretch')