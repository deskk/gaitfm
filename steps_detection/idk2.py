'''
Goal:

Load the same B3D file,
Read the JSON results from Script A to know which frames define a single gait cycle,
For each frame in that cycle, set the Nimble skeleton, read hip rotation, knee flexion, ankle rotation,
Plot the angles.

process:
loading those frame indices + Nimble skeleton + plotting angles.
'''

#!/usr/bin/env python

import json
import numpy as np
import matplotlib.pyplot as plt
import nimblephysics as nimble

def main():
    # -----------------------------------------------------
    # 1. LOAD JSON RESULTS FROM SCRIPT A
    # -----------------------------------------------------
    with open("event_detection_results.json", 'r') as f:
        results = json.load(f)
    b3d_path = results["b3d_path"]
    trial_index = results["trial_index"]
    hc_first = results["hc_first"]
    to_first = results["to_first"]
    fs = results["fs"]
    timestep_sec = results["timestep_sec"]
    print("Loaded event detection results:")
    print(results)

    # -----------------------------------------------------
    # 2. RE-LOAD THE B3D FILE & GET SKELETON
    # -----------------------------------------------------
    subject_on_disk = nimble.biomechanics.SubjectOnDisk(b3d_path)
    PROCESSING_PASS = 0  # same pass used in Script A (often "kinematics")
    skeleton = subject_on_disk.readSkel(processingPass=PROCESSING_PASS, ignoreGeometry=True)

    # Load frames for the same trial
    num_frames = subject_on_disk.getTrialLength(trial_index)
    frames = subject_on_disk.readFrames(
        trial=trial_index,
        startFrame=0,
        numFramesToRead=num_frames,
        includeSensorData=False,
        includeProcessingPasses=True
    )

    print(f"Trial {trial_index} has {num_frames} frames. We'll plot frames {hc_first} -> {to_first}.")

    # -----------------------------------------------------
    # 3. EXTRACT ANGLES (HIP ROT, KNEE FLEX, ANKLE ROT)
    # -----------------------------------------------------
    # We'll store time & angle arrays
    time_vals = []
    hip_rot_vals = []
    knee_flex_vals = []
    ankle_rot_vals = []

    # Suppose your model has:
    #  - "hip_left" with 3 coordinates: 
    #       index 2 -> internal/external rotation
    #  - "knee_left" with 1 coordinate (index 0) -> flexion
    #  - "ankle_left" with 1 coordinate (index 0) -> plantar/dorsiflex
    hip_joint = skeleton.getJoint("hip_left")
    knee_joint = skeleton.getJoint("knee_left")
    ankle_joint = skeleton.getJoint("ankle_left")

    for f_idx in range(hc_first, to_first + 1):
        if f_idx >= len(frames):
            break
        
        frame_data = frames[f_idx]
        pass_data = frame_data.processingPasses[PROCESSING_PASS]
        skeleton.setPositions(pass_data.pos)

        # Time relative to HC
        rel_time_sec = (f_idx - hc_first) * timestep_sec
        time_vals.append(rel_time_sec)

        # Hip rotation in degrees
        hip_rot_rad = hip_joint.getCoordinate(2).getValue(skeleton)  # might need to confirm index
        hip_rot_deg = np.degrees(hip_rot_rad)
        hip_rot_vals.append(hip_rot_deg)

        # Knee flexion in degrees
        knee_flex_rad = knee_joint.getCoordinate(0).getValue(skeleton)
        knee_flex_deg = np.degrees(knee_flex_rad)
        knee_flex_vals.append(knee_flex_deg)

        # Ankle rotation in degrees
        ankle_rot_rad = ankle_joint.getCoordinate(0).getValue(skeleton)
        ankle_rot_deg = np.degrees(ankle_rot_rad)
        ankle_rot_vals.append(ankle_rot_deg)

    # -----------------------------------------------------
    # 4. PLOT THE ANGLES
    # -----------------------------------------------------
    plt.figure(figsize=(8, 5))
    plt.plot(time_vals, hip_rot_vals,   label="Hip Rotation (deg)")
    plt.plot(time_vals, knee_flex_vals, label="Knee Flexion (deg)")
    plt.plot(time_vals, ankle_rot_vals, label="Ankle Rotation (deg)")
    plt.title("Gait Angles from First HC to First TO")
    plt.xlabel("Time (s) from Heel Contact")
    plt.ylabel("Angle (deg)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    print("Plot complete. Exiting.")

if __name__ == "__main__":
    main()
