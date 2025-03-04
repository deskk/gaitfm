'''
load b3d files with motion data, print # trials and specific trial
'''
import nimblephysics as nimble
from typing import List
import time

# Load the model, need absolute path
your_subject = nimble.biomechanics.SubjectOnDisk("/home/dkuan/Documents/research/gaitfm/data/Falisse2017_subject_1.b3d")

# Print the total number of trials in the subject
num_trials = your_subject.getNumTrials()
print(f"Total number of trials: {num_trials}")

# Read the skeleton that was optimized by the first process pass (always kinematics)
# Use the geometryFolder argument to specify where to load the bone mesh geometry from
skeleton: nimble.dynamics.Skeleton = your_subject.readSkel(
    processingPass=0,
    geometryFolder="/home/dkuan/Documents/research/gaitfm/Geometry/")

# Create a GUI
gui = nimble.NimbleGUI()

# Serve the GUI on port 8080
gui.serve(8080)
trial = 0

print(f"Viewing trial: {trial}")

trial_frames: List[nimble.biomechanics.Frame] = your_subject.readFrames(
    trial=trial,
    startFrame=0,
    numFramesToRead=your_subject.getTrialLength(trial))

# Figure out how many (fractional) seconds each frame represents
seconds_per_frame = your_subject.getTrialTimestep(trial)

# Loop through all the frames, and render them to the GUI
frame = 0
while True:
    # Get the frame we want to render
    frame_to_render = trial_frames[frame]

    # Set the skeleton's state to the state in the frame
    skeleton.setPositions(frame_to_render.processingPasses[0].pos)

    # Render the skeleton to the GUI
    gui.nativeAPI().renderSkeleton(skeleton)

    # Sleep for the appropriate amount of time
    time.sleep(seconds_per_frame)

    # Increment the frame counter
    frame += 1
    if frame >= len(trial_frames):
        frame = 0
