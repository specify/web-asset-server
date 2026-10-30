#!/usr/bin/env python3
"""Restart a Docker-unhealthy Compose service"""
import json
import os
import re
from pathlib import Path
import subprocess
import time


def container_state():
    container = subprocess.check_output(
        ['docker', 'compose', 'ps', '-q', 'asset-server'], text=True, timeout=10).strip()
    if not container:
        return None
    return json.loads(subprocess.check_output(
        ['docker', 'inspect', container], text=True, timeout=10))[0]['State']


def check(state_dir, cooldown=600):
    try:
        state = container_state()
    except subprocess.TimeoutExpired:
        print('Docker state query timed out; retrying on next timer run.', flush=True)
        return
    if not state or state.get('Health', {}).get('Status') != 'unhealthy':
        return
    now = time.time()
    marker = state_dir / 'last-attempt'
    last_attempt = float(marker.read_text()) if marker.exists() else 0
    if now - last_attempt < cooldown:
        print('Unhealthy; restart cooldown is still active.', flush=True)
        return
    # Count recent deployment restart toward the cooldown aswell
    from datetime import datetime
    started = state.get('StartedAt')
    if started:
        normalized = re.sub(r'(\.\d{6})\d+', r'\1', started.replace('Z', '+00:00'))
        started_at = datetime.fromisoformat(normalized).timestamp()
        if now - started_at < cooldown:
            return
    state_dir.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(now))
    print('Persistently unhealthy; restarting asset-server.', flush=True)
    subprocess.run(['docker', 'compose', 'restart', 'asset-server'], check=True, timeout=90)


if __name__ == '__main__':
    check(Path(os.environ.get('STATE_DIRECTORY', '/var/lib/asset-server-watchdog')),
          int(os.environ.get('COOLDOWN_SECONDS', '600')))
