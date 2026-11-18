"""
Generate 3 QR codes for the Python Assessment Portal (Basic, Intermediate, Advanced).

When students scan a QR code, their phone automatically receives a unique 10-question
assessment paper generated on-the-fly with both Scenario and Question.

Usage:
    python make_qr.py                           # Auto-detects local Wi-Fi/LAN IP on port 8501
    python make_qr.py http://192.168.1.50:8501 # Custom IP or domain
    python make_qr.py https://my-quiz-app.com   # Deployed domain
"""

import socket
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def get_local_ip():
    """Detect LAN IP address for phone connectivity over local Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# Determine base URL
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1].rstrip("/")
else:
    local_ip = get_local_ip()
    BASE_URL = f"http://{local_ip}:8501"

OUT_DIR = Path(__file__).parent / "qr_codes"
OUT_DIR.mkdir(exist_ok=True)

LEVELS = {
    "basic": "🟢 Basic Level (Conditionals)",
    "intermediate": "🟡 Intermediate Level (Functions, Decorators, Generators + Basic)",
    "advanced": "🔴 Advanced Level (OOP, Exceptions, Comprehensions, Lambda, Files + All)",
}

print(f"\n=======================================================")
print(f"📡 Generating 3 QR Codes for Base URL: {BASE_URL}")
print(f"=======================================================\n")

for level_key, level_name in LEVELS.items():
    # URL for this level (every scan generates unique random paper on phone)
    target_url = f"{BASE_URL}/?level={level_key}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_M,
        box_size=12,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    out_file = OUT_DIR / f"qr_{level_key}.png"
    img.save(out_file)

    print(f"[✓] {level_name}")
    print(f"    URL:  {target_url}")
    print(f"    File: {out_file.relative_to(Path(__file__).parent)}\n")

print(f"All 3 QR codes successfully generated in: {OUT_DIR.resolve()}\n")
