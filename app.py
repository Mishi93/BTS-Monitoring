import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="BTS Monitoring Dashboard",
    layout="wide"
)

# =========================================================
# LOAD TRAINED MODEL
# =========================================================

model = joblib.load("bts_failure_model.pkl")

# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>
        📡 Telecom BTS Monitoring Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# =========================================================
# SIDEBAR INPUTS
# =========================================================

st.sidebar.header("BTS Parameters")

location = st.sidebar.number_input(
    "Location ID",
    min_value=1,
    max_value=100,
    value=10
)

event_count = st.sidebar.slider(
    "Event Count",
    min_value=0,
    max_value=50,
    value=10
)

log_feature_count = st.sidebar.slider(
    "Log Feature Count",
    min_value=0,
    max_value=50,
    value=10
)

resource_type_count = st.sidebar.slider(
    "Resource Type Count",
    min_value=0,
    max_value=10,
    value=3
)

severity_type = st.sidebar.slider(
    "Severity Type",
    min_value=1,
    max_value=5,
    value=2
)

volume = st.sidebar.slider(
    "Log Volume",
    min_value=0,
    max_value=1000,
    value=100
)

# =========================================================
# INPUT DATA
# =========================================================

input_data = pd.DataFrame({
    "location": [location],
    "event_type": [event_count],
    "log_feature": [log_feature_count],
    "resource_type": [resource_type_count],
    "severity_type": [severity_type],
    "volume": [volume]
})

# =========================================================
# PREDICTION SECTION
# =========================================================

st.subheader("🤖 BTS Failure Prediction")

prediction = None
prob = None

if st.button("Predict BTS Fault"):

    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0]

    # -----------------------------------------------------
    # Input Data
    # -----------------------------------------------------

    st.markdown("### Input Data")

    st.dataframe(
        input_data,
        use_container_width=True
    )

    # -----------------------------------------------------
    # Prediction Result
    # -----------------------------------------------------

    if prediction == 0:

        st.success(
            "✅ BTS Operating Normally"
        )

    elif prediction == 1:

        st.warning(
            "⚠️ Minor Fault Detected"
        )

    else:

        st.error(
            "🚨 Major BTS Failure"
        )

    # -----------------------------------------------------
    # Probability Pie Chart
    # -----------------------------------------------------

    prob_df = pd.DataFrame({
        "Fault Type": [
            "No Fault",
            "Minor Fault",
            "Major Fault"
        ],
        "Probability": prob
    })

    fig_prob = px.pie(
        prob_df,
        names="Fault Type",
        values="Probability",
        title="Fault Probability",
        color="Fault Type",
        color_discrete_map={
            "No Fault": "green",
            "Minor Fault": "orange",
            "Major Fault": "red"
        }
    )

    fig_prob.update_traces(
        textinfo="percent+label",
        pull=[0.05, 0.05, 0.1]
    )

    st.plotly_chart(
        fig_prob,
        use_container_width=True
    )

    # -----------------------------------------------------
    # Alarm Panel
    # -----------------------------------------------------

    st.subheader("🚨 Network Alarm Panel")

    if prediction == 0:

        st.success(
            "No active alarms"
        )

    elif prediction == 1:

        st.warning(
            "Minor network alarm triggered"
        )

    else:

        st.error(
            "Critical BTS alarm – Immediate action required"
        )

st.markdown("---")

# =========================================================
# ACTIVITY & TREND CHARTS
# =========================================================

st.subheader("📈 BTS Activity & Fault Trend")

col1, col2 = st.columns(2)

# =========================================================
# ACTIVITY BAR CHART
# =========================================================

with col1:

    metrics = pd.DataFrame({
        "Feature": [
            "Events",
            "Logs",
            "Resources",
            "Severity",
            "Volume"
        ],
        "Value": [
            event_count,
            log_feature_count,
            resource_type_count,
            severity_type,
            volume
        ]
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

    fig_bar.update_layout(
        showlegend=False
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

# =========================================================
# FAULT TREND
# =========================================================

with col2:

    days = np.arange(1, 31)

    # Use prediction probability if available
    fault_rate = (
        prob[1] + prob[2]
        if prob is not None
        else 0.3
    )

    # Prevent an extremely high/low Poisson value
    fault_lambda = max(
        fault_rate * 5,
        0.1
    )

    np.random.seed(42)

    faults = np.random.poisson(
        lam=fault_lambda,
        size=30
    )

    trend_df = pd.DataFrame({
        "Day": days,
        "Faults": faults
    })

    fig_line = px.area(
        trend_df,
        x="Day",
        y="Faults",
        title="Monthly BTS Fault Trend",
        line_shape="spline",
        color_discrete_sequence=["#FF6F61"]
    )

    fig_line.update_traces(
        mode="lines+markers",
        marker=dict(size=8)
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

st.markdown("---")

# =========================================================
# NETWORK LOAD GAUGE
# =========================================================

st.subheader("📡 Network Load Gauge")

fig_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=volume,
        title={
            "text": "Network Load"
        },
        gauge={
            "axis": {
                "range": [0, 1000]
            },
            "bar": {
                "color": "#2E86C1"
            },
            "steps": [
                {
                    "range": [0, 500],
                    "color": "#ABEBC6"
                },
                {
                    "range": [500, 800],
                    "color": "#F9E79F"
                },
                {
                    "range": [800, 1000],
                    "color": "#F5B7B1"
                }
            ]
        }
    )
)

st.plotly_chart(
    fig_gauge,
    use_container_width=True
)

st.markdown("---")

# =========================================================
# BTS NETWORK RISK MAP
# =========================================================

st.subheader("🗺 BTS Network Risk Map")

# ---------------------------------------------------------
# Generate stable BTS coordinates
# ---------------------------------------------------------
# Using a fixed seed means BTS locations do not move
# whenever Streamlit reruns the application.

np.random.seed(42)

location_coords = {
    i: (
        24.80 + np.random.uniform(-0.12, 0.12),
        67.00 + np.random.uniform(-0.12, 0.12)
    )
    for i in range(1, 101)
}

# ---------------------------------------------------------
# Create BTS DataFrame
# ---------------------------------------------------------

bts_map_data = pd.DataFrame([
    {
        "location": loc_id,
        "latitude": lat,
        "longitude": lon
    }
    for loc_id, (lat, lon) in location_coords.items()
])

# ---------------------------------------------------------
# Generate fault probability
# ---------------------------------------------------------

np.random.seed(100)

bts_map_data["fault_prob"] = np.random.uniform(
    0,
    0.3,
    size=len(bts_map_data)
)

# ---------------------------------------------------------
# Apply actual model result to selected BTS
# ---------------------------------------------------------

if prob is not None:

    selected_fault_probability = (
        prob[1] + prob[2]
    )

    bts_map_data.loc[
        bts_map_data["location"] == location,
        "fault_prob"
    ] = selected_fault_probability

# ---------------------------------------------------------
# Convert probability to status
# ---------------------------------------------------------

def status_from_prob(probability):

    if probability < 0.1:
        return "Normal"

    elif probability < 0.3:
        return "Minor Fault"

    else:
        return "Major Fault"


bts_map_data["status"] = (
    bts_map_data["fault_prob"]
    .apply(status_from_prob)
)

# ---------------------------------------------------------
# Marker size
# ---------------------------------------------------------
# Keep most BTS markers approximately the same size.
# Selected BTS is made slightly larger.

bts_map_data["marker_size"] = 9

bts_map_data.loc[
    bts_map_data["location"] == location,
    "marker_size"
] = 16

# ---------------------------------------------------------
# Create Map
# ---------------------------------------------------------

fig_map = px.scatter_map(
    bts_map_data,
    lat="latitude",
    lon="longitude",
    color="status",
    size="marker_size",
    size_max=16,

    hover_name="location",

    hover_data={
        "latitude": ":.5f",
        "longitude": ":.5f",
        "fault_prob": ":.2%",
        "status": True,
        "marker_size": False
    },

    color_discrete_map={
        "Normal": "green",
        "Minor Fault": "orange",
        "Major Fault": "red"
    },

    zoom=9,
    height=600
)

# ---------------------------------------------------------
# Map Layout
# ---------------------------------------------------------

fig_map.update_layout(

    map_style="open-street-map",

    map_center={
        "lat": 24.80,
        "lon": 67.00
    },

    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0
    },

    legend_title_text="BTS Status"
)

# ---------------------------------------------------------
# Display Map
# ---------------------------------------------------------

st.plotly_chart(
    fig_map,
    use_container_width=True
)
