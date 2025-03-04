'''
read and parse c3d
format data to marker_traj dictionary
detect gait events
'''

# test_gait_event_detection.py
from gait_event_mocap_vu import ge_heel_toe_height, ge_mix

import c3d
import numpy as np
import matplotlib.pyplot as plt

# --- Function Definitions ---

def load_and_prepare_marker_traj(filepath):
    with open(filepath, 'rb') as handle:
        reader = c3d.Reader(handle)
        
        marker_traj = {}
        frame_rate = reader.header.frame_rate
        
        first_frame = next(reader.read_frames())
        marker_names = [reader.point_label(i) for i in range(len(first_frame[0]))]
        
        has_toe_marker = 'Toe' in marker_names
        has_metatarsal_marker = 'MT2' in marker_names
        if not has_toe_marker and not has_metatarsal_marker:
            raise ValueError("The data lacks both toe and 2nd metatarsal markers, necessary for gait analysis.")
        
        marker_data = {name: [] for name in marker_names}
        
        for points, _ in reader.read_frames():
            for i, point in enumerate(points):
                marker_data[marker_names[i]].append(point)
        
        for name, data in marker_data.items():
            marker_data[name] = np.array(data)
        
        marker_traj['heel_marker_y'] = marker_data['Heel'][:, 1]
        
        if has_toe_marker:
            marker_traj['toe_marker_y'] = marker_data['Toe'][:, 1]
            ge_method = 'ge_heel_toe_height'
        elif has_metatarsal_marker:
            marker_traj['toe_marker_z'] = marker_data['MT2'][:, 2]
            ge_method = 'ge_mix'
        
        marker_traj['sacrum_marker1_x'] = marker_data['Sacrum'][:, 0]
        marker_traj['sacrum_marker1_z'] = marker_data['Sacrum'][:, 2]
        marker_traj['sacrum_marker2_x'] = marker_data['Sacrum'][:, 0]
        marker_traj['sacrum_marker2_z'] = marker_data['Sacrum'][:, 2]
        
    return marker_traj, frame_rate, ge_method

def detect_gait_events(filepath, task='walking', vis=False):
    marker_traj, frame_rate, ge_method = load_and_prepare_marker_traj(filepath)
    
    if ge_method == 'ge_heel_toe_height':
        gait_events = ge_heel_toe_height(marker_traj, fs=frame_rate, vis=vis)
    elif ge_method == 'ge_mix':
        gait_events = ge_mix(marker_traj, fs=frame_rate, vis=vis, task=task)
    else:
        raise ValueError("Unsupported gait detection method.")
    
    return gait_events, frame_rate

def extract_single_gait_cycle(gait_events):
    hc_indices = gait_events['hc_index']
    
    if len(hc_indices) < 2:
        raise ValueError("Not enough heel contact events to define a full gait cycle.")
    
    gait_cycle_start = hc_indices[0]
    gait_cycle_end = hc_indices[1]
    
    return gait_cycle_start, gait_cycle_end

def plot_gait_cycle(marker_traj, start_frame, end_frame):
    heel_y = marker_traj['heel_marker_y']
    
    plt.figure()
    plt.plot(range(start_frame, end_frame), heel_y[start_frame:end_frame], label='Heel Y Position')
    plt.xlabel("Frame")
    plt.ylabel("Heel Y Position (Vertical)")
    plt.title("Heel Y Position During Single Gait Cycle")
    plt.legend()
    plt.show()

# --- Script Execution ---

# Replace 'gait01.c3d' with the path to your c3d file
filepath = 'gait01.c3d'

# Run gait event detection
try:
    gait_events, frame_rate = detect_gait_events(filepath, task='walking', vis=False)

    # Extract a single gait cycle
    gait_cycle_start, gait_cycle_end = extract_single_gait_cycle(gait_events)

    # Plot the single gait cycle
    marker_traj, _, _ = load_and_prepare_marker_traj(filepath)
    plot_gait_cycle(marker_traj, gait_cycle_start, gait_cycle_end)
    
except Exception as e:
    print(f"An error occurred: {e}")
