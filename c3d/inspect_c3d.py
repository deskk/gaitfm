import pybtk

def inspect_c3d_file(filepath):
    # Load the c3d file
    acq = pybtk.btkAcquisitionFileReader()
    acq.SetFilename(filepath)
    acq.Update()
    output = acq.GetOutput()

    # Print metadata (if available)
    print("File Metadata:")
    metadata = output.GetMetaData()
    for meta_key in metadata.GetChildNames():
        meta_data = metadata.GetChild(meta_key)
        print(f"  {meta_key}: {meta_data.GetInfo().ToString()}")

    # Print all marker names
    print("\nMarker Names:")
    for label in output.GetPointLabels():
        print(f"  {label}")

    # Optionally, print out the first few frames of data for each marker
    print("\nSample Data for First Marker (first 5 frames):")
    if output.GetPoints().GetItemNumber() > 0:
        marker_name = output.GetPointLabels()[0]
        marker_data = output.GetPoint(marker_name).GetValues()
        print(f"Marker '{marker_name}' Data:\n{marker_data[:5]}")

# Example usage:
inspect_c3d_file('gait01.c3d')
