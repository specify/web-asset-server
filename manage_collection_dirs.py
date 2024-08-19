# This can be given either a single name or a list of names
#
# ```bash
# python manage_collection_dirs.py add geo_swiss
# ```
# or 
# ```bash
# python3 manage_collection_dirs.py remove geo_swiss naag mcsn
# ```
#
# It creates new collection attachment directories. When a
# collection is removed, the directory and attachments remain.

import sys
import os
import subprocess

def add_collection_dir(collection_dir_names):
	# This creates a new directory for the collection
    attachments_dir = 'attachments'
    if not os.path.exists(attachments_dir):
        os.mkdir(attachments_dir)
    for collection_dir_name in collection_dir_names:
        dir_path = f'{attachments_dir}/{collection_dir_name}'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    with open("settings.py", "r+") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("COLLECTION_DIRS = {"):
                for collection_dir_name in collection_dir_names:
                    lines.insert(i+1, f"    '{collection_dir_name}': '{collection_dir_name}',\n")
                break
        f.seek(0)
        f.truncate()
        f.writelines(lines)

def remove_collection_dir(collection_dir_names):
    with open("settings.py", "r+") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            for collection_dir_name in collection_dir_names:
                if line.startswith(f"    '{collection_dir_name}': '{collection_dir_name}',"):
                    lines.pop(i)
                    break
        f.seek(0)
        f.truncate()
        f.writelines(lines)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python manage_collection_dirs.py add <collection_dir_name> [<collection_dir_name> ...]")
        print("Usage: python manage_collection_dirs.py remove <collection_dir_name> [<collection_dir_name> ...]")
    else:
        action = sys.argv[1]
        collection_dir_names = sys.argv[2:]
        if action == "add":
            add_collection_dir(collection_dir_names)
        elif action == "remove":
            remove_collection_dir(collection_dir_names)
        else:
            print("Invalid action. Use 'add' or 'remove'.")
    subprocess.run(['systemctl', 'restart', 'web-asset-server.service'])
