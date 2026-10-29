"""Alaprögzítés segítő nélkül: felvétel indul, a gyári program elindul,
képernyőkép készül, a program bezárul, a felvétel leáll."""

import subprocess
import sys
import time
from pathlib import Path

from PIL import ImageGrab

ROOT = Path(__file__).resolve().parent.parent
OEMDRV = r"C:\Program Files (x86)\AULA\F75\OemDrv.exe"

name = sys.argv[1] if len(sys.argv) > 1 else "01_alap_megnyitas"
shot = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "captures" / f"{name}.png"

capture = subprocess.Popen(
    [sys.executable, str(ROOT / "tools" / "capture.py"), name],
    stdin=subprocess.PIPE, text=True,
)
time.sleep(3)
app = subprocess.Popen([OEMDRV], cwd=str(Path(OEMDRV).parent))
time.sleep(15)
ImageGrab.grab(all_screens=True).save(shot)
print(f"Képernyőkép: {shot}", flush=True)

# Szabályos bezárás (WM_CLOSE), ha nem sikerül, kényszerített.
subprocess.run(["taskkill", "/PID", str(app.pid)], capture_output=True)
try:
    app.wait(timeout=10)
    print("A gyári program bezárult.", flush=True)
except subprocess.TimeoutExpired:
    subprocess.run(["taskkill", "/F", "/PID", str(app.pid)], capture_output=True)
    print("A gyári programot kényszerítve kellett bezárni.", flush=True)
time.sleep(2)

capture.communicate("\n")
sys.exit(capture.returncode)
