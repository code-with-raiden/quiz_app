import json
import sys
from pathlib import Path

import qrcode

# Usage: python make_qr.py https://your-domain.com
# Or edit the default below.
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
BASE_URL = BASE_URL.rstrip("/")

QUESTIONS_FILE = Path(__file__).parent / "questions.json"
OUT_DIR = Path(__file__).parent / "qr_codes"

OUT_DIR.mkdir(exist_ok=True)

with open(QUESTIONS_FILE, encoding="utf-8") as f:
    topics = json.load(f)["topics"]

for key, topic in topics.items():
    url = f"{BASE_URL}/topic/{key}"
    img = qrcode.make(url)
    path = OUT_DIR / f"qr_{key}.png"
    img.save(path)
    print(f"{topic['title']}: {url} -> {path.name}")
