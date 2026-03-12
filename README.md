📡 BTS Monitoring Dashboard

The BTS Monitoring Dashboard is an interactive web-based application that monitors and predicts the operational status of telecom Base Transceiver Stations (BTS). It combines machine learning predictions with interactive visualizations to help network engineers detect faults and manage BTS health proactively.

🛠 Features

Fault Prediction: Uses a pre-trained model to classify BTS as Normal, Minor Fault, or Major Fault.

Interactive Inputs: Users can set BTS parameters like location ID, event count, log features, resource type count, severity, and log volume.

Fault Probability Visualization: Pie chart showing the likelihood of each fault type.

Network Activity Dashboard: Bar chart for events, logs, resources, severity, and volume.

Fault Trend Analysis: Line/area chart showing historical fault trends over a month.

Network Load Gauge: Visualizes BTS log volume and highlights load levels.

Interactive BTS Map: Displays all BTS locations with color-coded markers for fault risk and size proportional to predicted probability. The selected BTS is prominently highlighted.

Alarm Panel: Displays warnings or critical alerts based on predictions.

🚀 Usage

Run the dashboard with:

streamlit run app.py

Use the sidebar to input BTS parameters.

Click Predict BTS Fault to see predictions, probability chart, and alarms.

Explore activity metrics, fault trends, network load, and the interactive BTS map.

📊 Visualizations

Activity Metrics: Bar chart for key BTS features.

Fault Trend: Area chart showing daily fault counts.

Network Load: Gauge visualization.

BTS Risk Map: Interactive map showing all towers with risk-based color coding and marker size.
