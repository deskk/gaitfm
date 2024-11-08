import nimblephysics as nimble

# Load the model absolute path
your_subject = nimble.biomechanics.SubjectOnDisk("/home/dkuan/Documents/research/gaitfm/Falisse2017_subject_1.b3d")
# Read the skeleton that was optimized by the first process pass (always kinematics)
# Use the geometryFolder argument to specify where to load the bone mesh geometry from
skeleton: nimble.dynamics.Skeleton = your_subject.readSkel(
    processingPass=0,
    geometryFolder="/home/dkuan/Documents/research/gaitfm/Geometry/")

# Create a GUI
gui = nimble.NimbleGUI()

# Serve the GUI on port #
gui.serve(8080)

# Render the skeleton to the GUI
gui.nativeAPI().renderSkeleton(skeleton)

# Block until the GUI is closed
gui.blockWhileServing()