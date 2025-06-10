import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import io

# Simulation parameters
num_parts = 144
plate_height = 5.5  # in inches
part_width = 1.5    # width of each part

# UI Inputs
st.title("Wire Cut Simulation for Vertically Printed Plates")

cut_from_top = st.radio("Wire cut starts from:", ["Top of the part", "Bottom (base of print)"])
cut_angle_deg = st.slider("Wire angle (degrees)", min_value=-5.0, max_value=5.0, value=0.0, step=0.1)
cut_angle_rad = np.deg2rad(cut_angle_deg)

tolerance_min = st.number_input("Tolerance minimum final height (inches)", min_value=0.0, max_value=plate_height, value=5.4, step=0.01)
tolerance_max = st.number_input("Tolerance maximum final height (inches)", min_value=0.0, max_value=plate_height, value=5.5, step=0.01)

start_height = plate_height if cut_from_top == "Top of the part" else 0.0

# Calculate final height of each part
x_positions = np.arange(num_parts)
if cut_from_top == "Top of the part":
    heights = plate_height - np.tan(cut_angle_rad) * x_positions * part_width
else:
    heights = np.tan(cut_angle_rad) * x_positions * part_width

# Clamp heights to valid range [0, plate_height]
heights = np.clip(heights, 0, plate_height)

# Plot the parts and cut line
fig, ax = plt.subplots(figsize=(12, 4))
colors = ['green' if tolerance_min <= h <= tolerance_max else 'red' for h in heights]
bars = ax.bar(x_positions, heights, width=0.9, color=colors)
ax.axhline(tolerance_min, color='blue', linestyle='--', label='Min Tolerance')
ax.axhline(tolerance_max, color='blue', linestyle='--', label='Max Tolerance')
ax.set_ylim(0, plate_height + 0.5)
ax.set_title("Simulated Final Heights After Wire Cut")
ax.set_xlabel("Part Index")
ax.set_ylabel("Final Height (inches)")
ax.legend()
st.pyplot(fig)

# Optional: Display list of out-of-tolerance parts
out_of_spec = np.where((heights < tolerance_min) | (heights > tolerance_max))[0]
if len(out_of_spec) > 0:
    st.warning(f"{len(out_of_spec)} parts are outside the tolerance window.")
    st.text(f"Out-of-spec part indices: {list(out_of_spec)}")
else:
    st.success("All parts are within tolerance.")

# Animated Simulation
def generate_animation():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, num_parts)
    ax.set_ylim(0, plate_height + 0.5)

    bars = ax.bar(x_positions, [plate_height] * num_parts, width=0.9, color='gray')
    wire_line, = ax.plot([], [], 'k-', linewidth=2)

    def init():
        wire_line.set_data([], [])
        return bars + (wire_line,)

    def animate(frame):
        wire_x = np.array([0, num_parts])
        if cut_from_top == "Top of the part":
            y_base = plate_height - frame / 100 * plate_height
        else:
            y_base = frame / 100 * plate_height

        # Apply angle
        y_wire = y_base + np.tan(cut_angle_rad) * (wire_x - 0)
        wire_line.set_data(wire_x, y_wire)

        for i, bar in enumerate(bars):
            if cut_from_top == "Top of the part":
                cut_height = plate_height - np.tan(cut_angle_rad) * i * part_width
            else:
                cut_height = np.tan(cut_angle_rad) * i * part_width
            cut_height = np.clip(cut_height, 0, plate_height)
            bar.set_height(cut_height)

        return bars + (wire_line,)

    anim = animation.FuncAnimation(
        fig, animate, init_func=init, frames=101, interval=30, blit=True
    )

    buf = io.BytesIO()
    writer = PillowWriter(fps=30)
    anim.save(buf, writer=writer)
    buf.seek(0)
    plt.close(fig)
    return buf

st.subheader("Wire Cutting Animation")
if st.button("Run Animation"):
    gif_bytes = generate_animation()
    st.image(gif_bytes, format="gif")
