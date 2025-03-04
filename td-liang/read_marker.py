import re

def print_marker_names(file_path):
    # Read the entire text file
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find all marker names that appear in <Marker name="...">
    pattern = re.compile(r'<Marker\s+name="([^"]+)">')
    markers = pattern.findall(text)

    # Print each marker name on its own line
    for marker in markers:
        print(marker)

if __name__ == "__main__":
    # Replace the path here with your file path
    print_marker_names('td-liang/markerset.txt')
