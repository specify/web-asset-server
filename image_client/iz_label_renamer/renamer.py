import os

# Define the root directory to start iteration
root_dir = '.'

# Walk through the directory hierarchy
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        filename = filename.lower()
        # Check if the filename matches the format "123456.jpg"
        if filename.endswith('.jpg') and filename[:-4].isdigit():
            print(f"Examining {filename}")
            # Construct the new filename with "CASIZ" prefix
            new_filename = f"CASIZ {filename}"
            old_filepath = os.path.join(dirpath, filename)
            new_filepath = os.path.join(dirpath, new_filename)

            # Rename the file
            os.rename(old_filepath, new_filepath)
            print(f'Renamed {old_filepath} to {new_filepath}')

