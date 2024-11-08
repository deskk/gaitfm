from scipy.io import loadmat

def load_mat(filepath):
    data = loadmat(filepath)
    # Assume the data has a specific field for markers
    # Accessing it might look like data['markers']
    markers = data['markers']
    # Convert to a format the script expects, for example, a dictionary
    marker_dict = {key: markers[key] for key in markers.dtype.names}
    return marker_dict
