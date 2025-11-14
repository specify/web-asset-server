#!/usr/bin/env python3
import sys
import subprocess
import re
import boto3
from urllib.parse import urlparse

SETTINGS_FILE = "settings.py"
SERVICE_NAME = "web-asset-server.service"  # adjust if different


def load_settings_contents():
    with open(SETTINGS_FILE, "r") as f:
        return f.readlines()


def write_settings_contents(lines):
    with open(SETTINGS_FILE, "w") as f:
        f.writelines(lines)


def parse_action_args():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python manage_collection_dirs.py add <collection> <s3://bucket/path> [<collection> <s3://bucket/path> ...]")
        print("  python manage_collection_dirs.py remove <collection> [<collection> ...]")
        sys.exit(1)
    action = sys.argv[1]
    args = sys.argv[2:]
    if action == "add":
        if len(args) % 2 != 0:
            print("For add, provide pairs: <collection> <s3://...> ...")
            sys.exit(1)
        pairs = [(args[i], args[i+1]) for i in range(0, len(args), 2)]
        return action, pairs
    elif action == "remove":
        names = args
        return action, names
    else:
        print("Invalid action. Use 'add' or 'remove'.")
        sys.exit(1)


def ensure_valid_s3_uri(uri):
    parsed = urlparse(uri)
    return parsed.scheme == "s3" and parsed.netloc


def add_collections(pairs):
    lines = load_settings_contents()
    # find COLLECTION_S3_PATHS block
    pattern = re.compile(r"^COLLECTION_S3_PATHS\s*=\s*{")
    start_idx = None
    for i, line in enumerate(lines):
        if pattern.match(line):
            start_idx = i
            break
    if start_idx is None:
        print("Couldn't find COLLECTION_S3_PATHS definition in settings.py")
        sys.exit(1)

    # find end of dict (matching closing brace)
    end_idx = start_idx
    brace_depth = 0
    for i in range(start_idx, len(lines)):
        if "{" in lines[i]:
            brace_depth += lines[i].count("{")
        if "}" in lines[i]:
            brace_depth -= lines[i].count("}")
            if brace_depth == 0:
                end_idx = i
                break
    # build existing entries map to avoid duplicates
    existing = {}
    for line in lines[start_idx+1:end_idx]:
        m = re.match(r"\s*['\"]([^'\"]+)['\"]\s*:\s*['\"]([^'\"]+)['\"],?", line)
        if m:
            existing[m.group(1)] = m.group(2)

    # insert or update entries
    insertion = []
    for coll, uri in pairs:
        if not ensure_valid_s3_uri(uri):
            print(f"Skipping invalid S3 URI for '{coll}': {uri}")
            continue
        if coll in existing:
            print(f"Updating existing collection '{coll}' to '{uri}'")
            # replace line in place later
            for i in range(start_idx+1, end_idx):
                if re.match(rf"\s*['\"]{re.escape(coll)}['\"]\s*:", lines[i]):
                    lines[i] = f"    '{coll}': '{uri}',\n"
                    break
        else:
            print(f"Adding collection '{coll}' -> '{uri}'")
            insertion.append(f"    '{coll}': '{uri}',\n")

    # inject new entries just before end_idx
    if insertion:
        lines = lines[:end_idx] + insertion + lines[end_idx:]

    write_settings_contents(lines)

    # create placeholder directories in S3 under originals/ and thumbnails/
    import settings as user_settings  # reload after edit
    s3 = boto3.client("s3")
    for coll, uri in pairs:
        if not ensure_valid_s3_uri(uri):
            continue
        bucket, base_prefix = parse_s3_uri(uri)
        for sub in (user_settings.ORIG_DIR, user_settings.THUMB_DIR):
            key_prefix = f"{base_prefix}/{sub}/"
            # create a zero-byte object to ensure the prefix is visible (not strictly needed)
            s3.put_object(Bucket=bucket, Key=key_prefix)


def remove_collections(names):
    lines = load_settings_contents()
    pattern = re.compile(r"^COLLECTION_S3_PATHS\s*=\s*{")
    start_idx = None
    for i, line in enumerate(lines):
        if pattern.match(line):
            start_idx = i
            break
    if start_idx is None:
        print("Couldn't find COLLECTION_S3_PATHS in settings.py")
        sys.exit(1)

    # locate end of dict
    end_idx = start_idx
    brace_depth = 0
    for i in range(start_idx, len(lines)):
        if "{" in lines[i]:
            brace_depth += lines[i].count("{")
        if "}" in lines[i]:
            brace_depth -= lines[i].count("}")
            if brace_depth == 0:
                end_idx = i
                break

    # filter out lines for the named collections
    new_block = []
    removed = []
    for line in lines[start_idx+1:end_idx]:
        skip = False
        for name in names:
            if re.match(rf"\s*['\"]{re.escape(name)}['\"]\s*:", line):
                skip = True
                removed.append(name)
                break
        if not skip:
            new_block.append(line)

    if not removed:
        print("No matching collections to remove found.")
        return

    # reconstruct file
    new_lines = lines[: start_idx+1] + new_block + lines[end_idx:]
    write_settings_contents(new_lines)
    print(f"Removed collections: {', '.join(removed)}")


def parse_s3_uri(s3_uri):
    parsed = urlparse(s3_uri)
    if parsed.scheme != 's3' or not parsed.netloc:
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/').rstrip('/')
    return bucket, prefix


if __name__ == "__main__":
    action, payload = parse_action_args()
    if action == "add":
        add_collections(payload)
    else:  # remove
        remove_collections(payload)

    # restart service
    subprocess.run(["systemctl", "restart", SERVICE_NAME])