'''
MAT file content recursive inspection
'''


import scipy.io
import numpy as np

def recursive_inspect(data, indent=0):
    """
    Recursively inspects nested structures in a MAT file.
    
    Parameters:
    - data: The data to inspect.
    - indent: Indentation level for pretty-printing nested structures.
    """
    # Check if data is a numpy void, which is typical for MATLAB structs
    if isinstance(data, np.void):
        for field_name in data.dtype.names:
            field_value = data[field_name]
            print(" " * indent + f"- Field '{field_name}': Type = {type(field_value)}, Shape = {getattr(field_value, 'shape', 'N/A')}")
            recursive_inspect(field_value, indent + 4)
    # If data is an ndarray, handle single-item arrays by unpacking
    elif isinstance(data, np.ndarray):
        # Check if it's a single-item array that might need unpacking
        if data.size == 1:
            print(" " * indent + "Single-item array, unpacking...")
            recursive_inspect(data[0], indent)
        elif data.dtype == object or data.dtype == np.void:
            for i, item in enumerate(data):
                print(" " * indent + f"[Array Item {i}]: Type = {type(item)}, Shape = {getattr(item, 'shape', 'N/A')}")
                recursive_inspect(item, indent + 4)
        else:
            print(" " * indent + f"Raw Data Array: Shape = {data.shape}")
    else:
        # Base case: if it's raw data, just print its type and shape
        print(" " * indent + f"Data: Type = {type(data)}, Shape = {getattr(data, 'shape', 'N/A')}")

def inspect_mat_file_recursive(mat_file_path, main_key='P01'):
    # Load the MAT file
    mat_data = scipy.io.loadmat(mat_file_path)
    
    # Check if the main key exists in the file
    main_data = mat_data.get(main_key)
    if main_data is None:
        print(f"Key '{main_key}' not found in the MAT file.")
        return
    
    # Start recursive inspection
    print(f"Inspecting '{main_key}': Type = {type(main_data)}, Shape = {main_data.shape}")
    recursive_inspect(main_data)

# Run the inspection with the actual file path
inspect_mat_file_recursive('P01.mat')
