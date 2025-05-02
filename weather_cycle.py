#!/usr/bin/env python3
import json
import os
from pathlib import Path

PROJECT_ROOT = Path.home() / "Projects" / "Weatherboy"
SPLIT_DIR = PROJECT_ROOT / "weather_data" / "split_days"
INDEX_FILE = PROJECT_ROOT / ".weather_cycle_index"

files = sorted(SPLIT_DIR.glob("*.json"))
if not files:
    exit(1)

try:
    idx = int(INDEX_FILE.read_text())
except:
    idx = 0

file = files[idx % len(files)]
idx = (idx + 1) % len(files)
INDEX_FILE.write_text(str(idx))

data = json.loads(file.read_text())

print(
    json.dumps(
        {
            "text": f"{data['weekday']}  Lo: {data['temp_min']}°F Hi: {data['temp_max']}°F {data['summary']}"
        }
    )
)
