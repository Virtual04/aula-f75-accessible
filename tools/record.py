"""Egy rögzítés a gyári program kezelésével, segítő nélkül.

    python tools\\record.py NEV X Y [X Y ...]

Elindítja a felvételt, sorban rákattint a megadott pontokra a gyári program
ablakában, ablakképet ment (captures\\NEV.png), majd leállítja a felvételt.
A gyári programnak már futnia kell, a megfelelő oldalon.
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import appwin  # noqa: E402

STOP = ROOT / "captures" / "STOP"


def main():
    name, coords = sys.argv[1], [int(c) for c in sys.argv[2:]]
    capture = subprocess.Popen(
        [sys.executable, str(ROOT / "tools" / "capture.py"), name, "--stop-file", str(STOP)],
        stdout=subprocess.PIPE, text=True, encoding="utf-8",
    )
    print(capture.stdout.readline().strip(), flush=True)
    time.sleep(2)
    for x, y in zip(coords[::2], coords[1::2]):
        appwin.click(x, y)
        time.sleep(1.5)
    time.sleep(2)
    appwin.shot(ROOT / "captures" / f"{name}.png")
    STOP.touch()
    print(capture.communicate()[0].strip())
    return capture.returncode


if __name__ == "__main__":
    sys.exit(main())
