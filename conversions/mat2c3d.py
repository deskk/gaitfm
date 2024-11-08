'''
convert MAT file to C3D file format
'''
import scipy.io
import ezc3d
import numpy as np

def extract_marker_data(nested_struct, paths):
    """
    Extracts marker data from specified paths within a nested structure.
    
    Parameters:
    - nested_struct: The main nested structure containing marker data.
    - paths: List of tuples, where each tuple represents a path to marker data.
    
    Returns:
    - marker_data: Concatenated marker data across specified paths.
    """
    marker_data = []
    
    for path in paths:
        data = nested_struct
        for field in path:
            data = data[field][0, 0]  # Traverse the path
        
        # Ensure the data is converted to a plain array, ignoring any field names
        if isinstance(data, np.ndarray) and data.dtype.names:
            data = np.array([list(d) for d in data])  # Convert structured array to plain numeric array
        
        # Append to marker data
        marker_data.append(data)
    
    # Concatenate into a single array
    return np.vstack(marker_data)

def mat_to_c3d(mat_file_path, c3d_file_path, frame_rate=100):
    # Load MAT file
    mat_data = scipy.io.loadmat(mat_file_path)
    
    # Extract nested structure under 'P01'
    main_struct = mat_data.get('P01')[0, 0]
    
    # Define paths to marker data for LeftFoot and RightFoot ambulation
    paths_to_marker_data = [
        ('LeftFoot_GaitCycle_Data', 'Level_Ground', 'Walking', 'Self_Selected_Speed'),
        ('LeftFoot_GaitCycle_Data', 'Level_Ground', 'Walking', 'Slow_Speed'),
        ('LeftFoot_GaitCycle_Data', 'Level_Ground', 'Walking', 'Fast_Speed'),
        ('RightFoot_GaitCycle_Data', 'Level_Ground', 'Walking', 'Self_Selected_Speed'),
        ('RightFoot_GaitCycle_Data', 'Level_Ground', 'Walking', 'Slow_Speed'),
        ('RightFoot_GaitCycle_Data', 'Level_Ground', 'Walking', 'Fast_Speed')
        # Add additional paths as necessary for Stairs_Ambulation, Ramp_Ambulation, etc.
    ]
    
    # Extract marker data and reshape it to (num_frames, num_markers, 3)
    marker_data = extract_marker_data(main_struct, paths_to_marker_data)
    num_frames = marker_data.shape[0] // 3
    marker_data = marker_data.reshape((num_frames, -1, 3))
    num_markers = marker_data.shape[1]
    
    # Initialize a new C3D object
    c3d = ezc3d.c3d()
    
    # Set C3D parameters
    c3d['parameters']['POINT']['RATE'].value = [frame_rate]
    c3d['parameters']['POINT']['FRAMES'].value = [num_frames]
    c3d['parameters']['POINT']['USED'].value = [num_markers]
    
    # Populate marker data frame by frame
    for frame in range(num_frames):
        frame_points = marker_data[frame]
        c3d['data']['points'][:, frame, :num_markers] = frame_points.T
    
    # Save the C3D file
    c3d.write(c3d_file_path)
    print(f"C3D file saved as {c3d_file_path}")

# Usage
mat_file_path = '/home/dkuan/Documents/research/gaitfm/P01.mat'
c3d_file_path = '/home/dkuan/Documents/research/gaitfm/dimitrov_P01.c3d'
mat_to_c3d(mat_file_path, c3d_file_path)
