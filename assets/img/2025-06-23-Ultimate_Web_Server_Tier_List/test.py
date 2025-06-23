import os
import sys
from PIL import Image

# Check for command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <directory>")
    sys.exit(1)

directory = sys.argv[1]

# Check if the given path is a directory
if not os.path.isdir(directory):
    print(f"Error: '{directory}' is not a directory.")
    sys.exit(1)

# Set of target filenames (without extensions)
target_names = {f'photo{i}' for i in range(1, 6)}

# Loop over files in the directory
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
        name, _ = os.path.splitext(filename)
        if name in target_names:
            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                markdown_str = f'![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/{directory}/{filename}){{: width="{width}" height="{height}" }}'
                print(markdown_str)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

