
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("Wire Cut Simulation for Vertically Printed Plates")

# Sidebar inputs
st.sidebar.header("Simulation Parameters")
num_plates = st.sidebar.number_input("Number of Plates", min_value=1, max_value=500, value=144)
plate_height = st.sidebar.number_input("Plate Height (in)", min_value=0.1, max_value=10.0, value=5.5)
plate_width = st.sidebar.number_input("Plate Width (in)", min_value=0.1, max_value=5.0, value=1.5)
tolerance_low = st.sidebar.number_input("Min Tolerance Height (in)", min_value=0.0, max_value=10.0, value=5.48)
tolerance_high = st.sidebar.number_input("Max Tolerance Height (in)", min_value=0.0, max_value=10.0, value=5.52)
wire_angle_deg = st.sidebar.slider("Wire Cut Angle (degrees)", min_value=-5.0, max_value=5.0, value=0.0, step=0.01)

# Simulation logic
angle_rad = np.deg2rad(wire_angle_deg)
cut_variation = np.tan(angle_rad) * plate_width
heights = np.full(num_plates, plate_height - cut_variation)

status = np.where((heights >= tolerance_low) & (heights <= tolerance_high), "PASS", "FAIL")

df = pd.DataFrame({
    "Plate #": np.arange(1, num_plates + 1),
    "Final Height (in)": heights,
    "Status": status
})

# Display results
st.subheader("Simulation Results")
st.dataframe(df)

# Visualization
st.subheader("Cut Height Visualization")
fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar(df["Plate #"], df["Final Height (in)"], color=(df["Status"] == "PASS").map({True: "green", False: "red"}))
ax.axhline(tolerance_low, color='blue', linestyle='--', label='Min Tolerance')
ax.axhline(tolerance_high, color='blue', linestyle='--', label='Max Tolerance')
ax.set_xlabel("Plate Number")
ax.set_ylabel("Height After Cut (in)")
ax.set_title("Plate Height After Wire Cut")
ax.legend()
st.pyplot(fig)

# Download
csv = df.to_csv(index=False)
st.download_button("Download Results as CSV", data=csv, file_name="cut_simulation_results.csv", mime="text/csv")
