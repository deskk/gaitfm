#!/usr/bin/env python

'''
Loads your B3D trial,
Builds a Pandas DataFrame from select marker columns,
Calls our new self-contained angle-based event detection function,
Saves a single gait cycle (heel-contact → toe-off) to JSON (or you can adapt as needed).
python
Copy code

'''



"""
Script A: Extract gait events using angle-based filtering, and save event frames.

1) Load a B3D file (Nimble) to get marker data.
2) Convert relevant markers into a Pandas DataFrame (just for ease of manipulation).
3) Run angle-based detection (heel + toe + sacrum vectors).
4) Save the chosen step(s) to a JSON.
"""

import numpy as np
import pandas as pd
import json
import nimblephysics as nimble

from gait_event_mocap_dk import detect_heel_toe_with_angle

def main():
    # ----------------------------------------------------------------
    # 1. LOAD YOUR B3D SUBJECT + TRIAL
    # ----------------------------------------------------------------
    b3d_path = "/home/dkuan/Documents/research/gaitfm/steps_detection/SN001-test-liangmodel-1.b3d"  # Adjust path
    subject_on_disk = nimble.biomechanics.SubjectOnDisk(b3d_path)

    trial_index = 0
    num_trials = subject_on_disk.getNumTrials()
    print(f"Total trials: {num_trials}. Using trial={trial_index}, name={subject_on_disk.getTrialName(trial_index)}")

    num_frames = subject_on_disk.getTrialLength(trial_index)
    timestep_sec = subject_on_disk.getTrialTimestep(trial_index)
    fs = int(round(1.0 / timestep_sec))
    print(f"Trial {trial_index} => {num_frames} frames at {fs} Hz (dt={timestep_sec:.4f}s)")

    # Read frames to get marker data
    frames = subject_on_disk.readFrames(
        trial=trial_index,
        startFrame=0,
        numFramesToRead=num_frames,
        includeSensorData=True,
        includeProcessingPasses=False
    )

    # ----------------------------------------------------------------
    # 2. BUILD A PANDAS DATAFRAME WITH MARKER COLUMNS
    #    (We'll collect: heel_y, toe_y, sacrum_marker1_x, sacrum_marker1_z, sacrum_marker2_x, sacrum_marker2_z)
    # ----------------------------------------------------------------
    # For the angle-based logic, the original code used:
    #   - heel_marker_y   = ...
    #   - toe_marker_y    = ...
    #   - sacrum_marker1_x, sacrum_marker1_z
    #   - sacrum_marker2_x, sacrum_marker2_z
    #
    # Let's assume your B3D has marker names "LeftCAL", "LeftTOE", "Sacrum1", "Sacrum2".
    # You will need to adapt these to match whatever is in your dataset.
    marker_map = {
        "LeftCAL": "heel",
        "LeftTOE": "toe",
        # We'll pretend we have "Sacrum1" and "Sacrum2" for that angle logic
        "Sacrum1": "sacrum1",
        "Sacrum2": "sacrum2"
    }

    # Set up columns for the DataFrame
    df_dict = {
        "heel_marker_y": [],
        "toe_marker_y": [],
        "sacrum_marker1_x": [],
        "sacrum_marker1_z": [],
        "sacrum_marker2_x": [],
        "sacrum_marker2_z": []
    }

    for frame in frames:
        marker_dict = {m_name: m_pos for (m_name, m_pos) in frame.markerObservations}

        # Fill each column. If missing, set to np.nan
        # HEEL => Y
        if "LeftCAL" in marker_dict:
            df_dict["heel_marker_y"].append(marker_dict["LeftCAL"][1])
        else:
            df_dict["heel_marker_y"].append(np.nan)

        # TOE => Y
        if "LeftTOE" in marker_dict:
            df_dict["toe_marker_y"].append(marker_dict["LeftTOE"][1])
        else:
            df_dict["toe_marker_y"].append(np.nan)

        # Sacrum1 => X,Z
        if "Sacrum1" in marker_dict:
            df_dict["sacrum_marker1_x"].append(marker_dict["Sacrum1"][0])
            df_dict["sacrum_marker1_z"].append(marker_dict["Sacrum1"][2])
        else:
            df_dict["sacrum_marker1_x"].append(np.nan)
            df_dict["sacrum_marker1_z"].append(np.nan)

        # Sacrum2 => X,Z
        if "Sacrum2" in marker_dict:
            df_dict["sacrum_marker2_x"].append(marker_dict["Sacrum2"][0])
            df_dict["sacrum_marker2_z"].append(marker_dict["Sacrum2"][2])
        else:
            df_dict["sacrum_marker2_x"].append(np.nan)
            df_dict["sacrum_marker2_z"].append(np.nan)

    df_mocap = pd.DataFrame(df_dict)

    # ----------------------------------------------------------------
    # 3. DETECT EVENTS USING ANGLE-BASED FUNCTION
    # ----------------------------------------------------------------
    events = detect_heel_toe_with_angle(
        df_mocap["heel_marker_y"].values,
        df_mocap["toe_marker_y"].values,
        df_mocap["sacrum_marker1_x"].values,
        df_mocap["sacrum_marker1_z"].values,
        df_mocap["sacrum_marker2_x"].values,
        df_mocap["sacrum_marker2_z"].values,
        fs=fs,
        min_time_between_events=0.6,
        angle_thresh_deg=90,
        print_debug=True
    )

    hc_indices = events["hc_index"]
    to_indices = events["to_index"]
    print("Detected heel contacts:", hc_indices)
    print("Detected toe offs:", to_indices)

    # Pick the first cycle
    if len(hc_indices) == 0 or len(to_indices) == 0:
        print("No events found. Exiting.")
        return
    first_hc = hc_indices[0]
    # find a to that is after the first hc
    to_after = to_indices[to_indices > first_hc]
    if len(to_after) == 0:
        print("No toe-off after first HC. Exiting.")
        return
    first_to = to_after[0]

    print(f"Chosen cycle: frames {first_hc} -> {first_to}")

    # Save results to JSON for use in a follow-up script
    output_data = {
        "b3d_path": b3d_path,
        "trial_index": trial_index,
        "fs": fs,
        "hc_first": int(first_hc),
        "to_first": int(first_to)
    }

    out_json = "event_detection_results.json"
    with open(out_json, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSaved event detection results to '{out_json}'\nDone.")

if __name__ == "__main__":
    main()
