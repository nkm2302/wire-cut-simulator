import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import io

st.set_page_config(page_title="Wire Cut Simulation", layout="wide")

st.title("Wire Cut Simulation on Vertically Printed Plates")

# --- User Inputs ---
num_plates = st.number_input("Number of plates", min_value=1, max_value=200, value=144, step=1)
plate_height = st.number_input("Plate height (inches)", min_value=0.1, max_value=20.0, value=5.5, step=0.1)
plate_width = st.number_input("Plate width (inches)", min_value=0.1, max_value=10.0, value=1.5, step=0.1)

cut_offset_top = st.number_input("Cut offset from top of stack (inches)", min_value=0.0, max_value=plate_height*num_plates, value=0.5, step=0.1)
wire_angle_deg = st.slider("Wire angle (degrees, positive tilts cutting line downward to right)", min_value=-5.0, max_value=5.0, value=0.0, step=0.1)

tol_min = st.number_input("Tolerance minimum final height (inches)", min_value=0.0, max_value=plate_height, value=5.4, step=0.01)
tol_max = st.number_input("Tolerance maximum final height (inches)", min_value=0.0, max_value=plate_height, value=5.5, step=0.01)

# --- Calculate final cut heights ---
angle_rad = np.deg2rad(wire_angle_deg)
slope = np.tan(angle_rad)

# For each plate i (0-indexed from bottom plate),
# Calculate how far wire intersects it.
# Stack height coordinates:
# plate bottom = i * plate_height
# plate top = (i+1) * plate_height
# The wire line y = cut_offset_top + slope * (x - x_start)
# We want to find the height at x=plate_width (right edge), which determines how deep the wire cuts vertically in each plate

# Since wire moves from x_start horizontally, assume x_start=0 for calculation of final height
# The vertical cut line at x=plate_width:
# y_at_plate_width = cut_offset_top + slope * plate_width

# We find the intersection height within each plate from the top:
# For plate i, final height = plate_height - (cut height relative to plate bottom)

# Let's compute the vertical height at plate base (y= i*plate_height)
# and the wire height at the right edge

# The vertical position of the wire changes linearly as it moves down the stack, so calculate the wire height at each plate level

wire_heights_at_left = cut_offset_top  # wire starting height at x=0
wire_heights_at_right = cut_offset_top + slope * plate_width  # wire height at x=plate_width

# Linear interpolation of wire height from left to right edge over width:
# To simplify, assume cut height is uniform across width at the cut offset from top + angle slope

# So at plate i, the cut height from top is:
# cut_height_at_plate_i = wire_heights_at_left - i * plate_height

# But since slope affects vertical at x=plate_width, we calculate wire height per plate as average:

final_heights = []
for i in range(num_plates):
    # Calculate wire height at the bottom of plate i
    plate_bottom_height = i * plate_height
    # Wire height at x=0 for this plate bottom level:
    wire_height_at_plate_bottom_left = wire_heights_at_left - plate_bottom_height
    # Wire height at x=plate_width for this plate bottom level:
    wire_height_at_plate_bottom_right = wire_heights_at_right - plate_bottom_height
    # Average wire height across width for this plate bottom:
    wire_height_at_plate_bottom_avg = (wire_height_at_plate_bottom_left + wire_height_at_plate_bottom_right) / 2

    # Final height of plate after cut (height left) is:
    height_left = max(0, wire_height_at_plate_bottom_avg)
    # Clamp to max plate height
    height_left = min(height_left, plate_height)
    final_heights.append(height_left)

df = pd.DataFrame({
    "Plate #": np.arange(1, num_plates+1),
    "Final Height (in)": final_heights,
    "Pass": [(tol_min <= h <= tol_max) for h in final_heights]
})

# --- Display table ---
st.subheader("Final Heights After Wire Cut")
st.dataframe(df.style.applymap(lambda val: 'background-color: lightgreen' if val==True else 'background-color: salmon', subset=["Pass"]))

# --- Bar chart ---
fig, ax = plt.subplots(figsize=(10, 4))
colors = ['green' if p else 'red' for p in df["Pass"]]
ax.bar(df["Plate #"], df["Final Height (in)"], color=colors)
ax.axhline(tol_min, color='blue', linestyle='--', label='Tolerance Min')
ax.axhline(tol_max, color='blue', linestyle='--', label='Tolerance Max')
ax.set_xlabel("Plate Number")
ax.set_ylabel("Final Height (inches)")
ax.set_title("Final Height of Each Plate After Cut")
ax.legend()
st.pyplot(fig)

# --- Animation ---

def generate_animation():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, plate_width + 1)
    ax.set_ylim(0, plate_height * num_plates)
    ax.invert_yaxis()
    ax.set_title("Wire Cutting Animation")
    ax.set_xlabel("Width (inches)")
    ax.set_ylabel("Height (inches from top)")

    # Draw plates
    plates = []
    for i in range(num_plates):
        rect = plt.Rectangle((0, i * plate_height), plate_width, plate_height, fill=True, color='lightgray', ec='black')
        plates.append(rect)
        ax.add_patch(rect)

    wire_line, = ax.plot([], [], color='red', linewidth=3)

    def init():
        wire_line.set_data([], [])
        return (wire_line,)

    def animate(frame):
        # frame goes from 0 to 100
        x_start = frame * (plate_width / 100)
        x_vals = np.array([x_start, plate_width])
        y_vals = cut_offset_top + slope * (x_vals - x_start)
        y_vals = np.clip(y_vals, 0, plate_height * num_plates)
        wire_line.set_data(x_vals, y_vals)
        return (wire_line,)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=101, interval=30, blit=True)

    buf = io.BytesIO()
   from matplotlib.animation import PillowWriter

    writer = PillowWriter(fps=30)
    anim.save(buf, writer=writer)
    buf.seek(0)
    plt.close(fig)
    return buf


st.subheader("Wire Cut Process Animation")
gif_bytes = generate_animation()
st.image(gif_bytes, width=700)
