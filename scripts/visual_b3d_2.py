'''
load all trials, print # of trials
'''
import nimblephysics as nimble
from typing import List
import time

# Load the model, need absolute path
your_subject = nimble.biomechanics.SubjectOnDisk("/home/dkuan/Documents/research/gaitfm/steps_detection/SN001-test-liangmodel-1.b3d")

# Print the total number of trials for this subject
num_trials = your_subject.getNumTrials()
print(f"Number of trials available: {num_trials}")

# Read the skeleton that was optimized by the first process pass (always kinematics)
# Use the geometryFolder argument to specify where to load the bone mesh geometry from
skeleton: nimble.dynamics.Skeleton = your_subject.readSkel(
    processingPass=0,
    geometryFolder="/home/dkuan/Documents/research/gaitfm/Geometry/")

# Create a GUI
gui = nimble.NimbleGUI()

# Serve the GUI on port 8080
gui.serve(8080)

def load_and_render_trial(trial_number: int):
    """
    Load the frames for the specified trial and render them in a loop.
    """
    print(f"Loading trial {trial_number}...")
    
    # Load all the frames from the selected trial
    trial_frames: List[nimble.biomechanics.Frame] = your_subject.readFrames(
        trial=trial_number,
        startFrame=0,
        numFramesToRead=your_subject.getTrialLength(trial_number))

    # Figure out how many (fractional) seconds each frame represents
    seconds_per_frame = your_subject.getTrialTimestep(trial_number)

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
            frame = 0  # Restart loop for playback

        # Check for user input to switch trials
        if gui.nativeAPI().hasMessage():
            message = gui.nativeAPI().getNextMessage()
            if message.startswith("trial:"):
                new_trial = int(message.split(":")[1])
                print(f"Switching to trial {new_trial}...")
                return new_trial

# Main loop for dynamic trial loading
current_trial = 0
while True:
    # Print the current trial being displayed
    print(f"Currently displaying trial {current_trial}.")
    
    # Load and render the current trial
    current_trial = load_and_render_trial(current_trial)
