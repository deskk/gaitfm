#!/usr/bin/env python

"""
angle_event_detection.py

Self-contained angle-based detection of heel contact (HC) and toe off (TO).
Replicates the logic in the original "gait_event_mocap.py" code, but
without external dependencies.

Core steps:
1) Find local minima in heel (HC) and toe (TO) signals, using find_peaks() on -1*marker_y.
2) Filter out spurious events by checking the angle between sacrum_marker1 - sacrum_marker2
   at consecutive events. If angle < angle_thresh_deg, we keep it.

We do not do any fancy corrections (eric_lauren_correction / vu_correction) here,
just the angle-based filter.
"""

import numpy as np
from scipy.signal import find_peaks

def angle_between_vectors(v1, v2):
    """
    Calculate the angle (in degrees) between two 2D vectors v1 and v2.
    """
    v1 = np.array(v1, dtype=float)
    v2 = np.array(v2, dtype=float)
    dot_val = np.dot(v1, v2)
    norms   = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norms < 1e-12:
        return 0.0
    angle_rad = np.arccos(dot_val / norms)
    return np.degrees(np.abs(angle_rad))

def detect_heel_toe_with_angle(
    heel_marker_y,
    toe_marker_y,
    sacrum_marker1_x,
    sacrum_marker1_z,
    sacrum_marker2_x,
    sacrum_marker2_z,
    fs=100,
    min_time_between_events=0.6,
    angle_thresh_deg=90,
    print_debug=False
):
    """
    Replicates the "heel-toe height" method from the original script, including
    sacrum-based angle filtering.

    Args:
        heel_marker_y (array-like): vertical positions of heel marker
        toe_marker_y  (array-like): vertical positions of toe marker
        sacrum_marker1_x (array-like): X coords for sacrum marker1
        sacrum_marker1_z (array-like): Z coords for sacrum marker1
        sacrum_marker2_x (array-like): X coords for sacrum marker2
        sacrum_marker2_z (array-like): Z coords for sacrum marker2

        fs (int): sampling rate in Hz
        min_time_between_events (float): minimum time (in seconds) between consecutive HCs or TOs
        angle_thresh_deg (float): if the angle between consecutive sacrum vectors is < this, we keep the event
        print_debug (bool): if True, prints debugging info

    Returns:
        gait_events (dict):
            {
              'hc_index': np.array([...]),
              'hc_value': np.array([...]),
              'to_index': np.array([...]),
              'to_value': np.array([...])
            }
    """
    heel_y = np.array(heel_marker_y, dtype=float)
    toe_y  = np.array(toe_marker_y,  dtype=float)

    # Invert signals => local minima become local maxima
    inv_heel = -1 * heel_y
    inv_toe  = -1 * toe_y

    # Minimum distance in samples
    min_samples = int(round(min_time_between_events * fs))

    # 1) Find potential heel contacts
    hc_indices, hc_props = find_peaks(
        inv_heel, distance=min_samples, height=(-1, 0)
    )
    hc_values = inv_heel[hc_indices]  # these are the inverted peaks

    # 2) Filter them by sacrum angle
    #    We'll replicate the "for i in range(1, len(temp_hc_index))" approach:
    #    keep event i if angle < angle_thresh_deg w.r.t. event (i-1).
    #    Note: the original code constructs 2D vectors from (x1,z1) - (x2,z2).

    filtered_hc_indices = []
    filtered_hc_values  = []
    for i in range(1, len(hc_indices)):
        prev_idx = hc_indices[i - 1]
        curr_idx = hc_indices[i]

        prev_vec = [
            sacrum_marker1_x[prev_idx] - sacrum_marker2_x[prev_idx],
            sacrum_marker1_z[prev_idx] - sacrum_marker2_z[prev_idx]
        ]
        curr_vec = [
            sacrum_marker1_x[curr_idx] - sacrum_marker2_x[curr_idx],
            sacrum_marker1_z[curr_idx] - sacrum_marker2_z[curr_idx]
        ]
        angle = angle_between_vectors(prev_vec, curr_vec)
        if angle < angle_thresh_deg:
            filtered_hc_indices.append(curr_idx)
            filtered_hc_values.append(inv_heel[curr_idx])

    # 3) Find potential toe offs
    to_indices, to_props = find_peaks(
        inv_toe, distance=min_samples, height=(-1, 0)
    )
    to_values = inv_toe[to_indices]

    # Filter them with the same sacrum angle approach
    filtered_to_indices = []
    filtered_to_values  = []
    for i in range(1, len(to_indices)):
        prev_idx = to_indices[i - 1]
        curr_idx = to_indices[i]

        prev_vec = [
            sacrum_marker1_x[prev_idx] - sacrum_marker2_x[prev_idx],
            sacrum_marker1_z[prev_idx] - sacrum_marker2_z[prev_idx]
        ]
        curr_vec = [
            sacrum_marker1_x[curr_idx] - sacrum_marker2_x[curr_idx],
            sacrum_marker1_z[curr_idx] - sacrum_marker2_z[curr_idx]
        ]
        angle = angle_between_vectors(prev_vec, curr_vec)
        if angle < angle_thresh_deg:
            filtered_to_indices.append(curr_idx)
            filtered_to_values.append(inv_toe[curr_idx])

    if print_debug:
        print(f"[DEBUG] Original HC candidates: {hc_indices}")
        print(f"[DEBUG] Filtered HC indices: {filtered_hc_indices}")
        print(f"[DEBUG] Original TO candidates: {to_indices}")
        print(f"[DEBUG] Filtered TO indices: {filtered_to_indices}")

    # Build dict
    gait_events = {
        'hc_index': np.array(filtered_hc_indices, dtype=int),
        'hc_value': np.array(filtered_hc_values, dtype=float),
        'to_index': np.array(filtered_to_indices, dtype=int),
        'to_value': np.array(filtered_to_values, dtype=float),
    }
    return gait_events


def demo_run():
    """
    Quick demonstration with random signals, to show how the function is called.
    In real usage, you'll import detect_heel_toe_with_angle() in your scripts.
    """
    import matplotlib.pyplot as plt

    fs = 100
    n  = 500
    t  = np.linspace(0, 2*np.pi, n)

    # Synthetic marker signals
    heel_y = 0.2 - 0.1 * np.sin(t * 2)
    toe_y  = 0.1 - 0.08 * np.sin(t * 2.1)

    # We'll just define sacrum1 and sacrum2 so the angle is random
    # (Hence, events may get filtered out unpredictably in a real scenario.)
    sacrum_marker1_x = np.random.rand(n) * 0.5
    sacrum_marker1_z = np.random.rand(n) * 0.5
    sacrum_marker2_x = np.random.rand(n) * 0.5
    sacrum_marker2_z = np.random.rand(n) * 0.5

    events = detect_heel_toe_with_angle(
        heel_marker_y=heel_y,
        toe_marker_y=toe_y,
        sacrum_marker1_x=sacrum_marker1_x,
        sacrum_marker1_z=sacrum_marker1_z,
        sacrum_marker2_x=sacrum_marker2_x,
        sacrum_marker2_z=sacrum_marker2_z,
        fs=fs,
        min_time_between_events=0.3,
        angle_thresh_deg=90,
        print_debug=True
    )

    hc = events["hc_index"]
    to = events["to_index"]

    # Plot
    plt.figure()
    plt.plot(heel_y, label="heel_y")
    plt.plot(toe_y,  label="toe_y")
    plt.scatter(hc, heel_y[hc], color='r', label="HC (filtered)")
    plt.scatter(to, toe_y[to], color='g',  label="TO (filtered)")
    plt.legend()
    plt.title("Demo angle-based detection")
    plt.show()

if __name__ == "__main__":
    demo_run()
