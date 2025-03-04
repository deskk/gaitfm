# import nimblephysics as nimble
# from typing import List
# import time

# # Load the B3D
# your_subject = nimble.biomechanics.SubjectOnDisk("/home/dkuan/Documents/research/gaitfm/data/Falisse2017_subject_1.b3d")

# # Create the skeleton from pass=0 if you want (this is readSkel(), which is still valid)
# skeleton: nimble.dynamics.Skeleton = your_subject.readSkel(
#     processingPass=0,
#     geometryFolder="/home/dkuan/Documents/research/gaitfm/Geometry/",
#     ignoreGeometry=False
# )

# # Create a GUI
# gui = nimble.NimbleGUI()
# gui.serve(8080)

# trial = 0

# # ** No more 'processingPass=0' in readFrames **
# trial_frames: List[nimble.biomechanics.Frame] = your_subject.readFrames(
#     trial=trial,
#     startFrame=0,
#     numFramesToRead=your_subject.getTrialLength(trial),
#     includeSensorData=False,      # or True, up to you
#     includeProcessingPasses=True  # so we can access processingPasses[0]
# )

# seconds_per_frame = your_subject.getTrialTimestep(trial)

# frame = 0
# while True:
#     frame_to_render = trial_frames[frame]

#     # If we want the pose from pass=0, we do:
#     pass_data = frame_to_render.processingPasses[0]  # or [1], etc.
#     skeleton.setPositions(pass_data.pos)

#     gui.nativeAPI().renderSkeleton(skeleton)
#     time.sleep(seconds_per_frame)

#     frame += 1
#     if frame >= len(trial_frames):
#         frame = 0


import nimblephysics as nimble

subject = nimble.biomechanics.SubjectOnDisk("/home/dkuan/Documents/research/gaitfm/data/gait01.c3d")

skeleton = subject.readSkel(processingPass=0, ignoreGeometry=True)
trial_index = 0
num_frames = subject.getTrialLength(trial_index)

frames = subject.readFrames(
    trial=trial_index,
    startFrame=0,
    numFramesToRead=num_frames,
    includeSensorData=True,
    includeProcessingPasses=True
)

print(f"Loaded {len(frames)} frames. Attempting to set skeleton positions...")

for i, frame in enumerate(frames):
    # pick pass 0 or 1
    pass_data = frame.processingPasses[0]
    skeleton.setPositions(pass_data.pos)
    if i % 50 == 0:
        print(f"Frame {i} setPositions OK")

print("No segfault => likely GUI or geometry issue.")
