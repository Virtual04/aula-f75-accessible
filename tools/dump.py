"""Egy felvétel konfigurációs csomagjainak kiírása, soronként egy csomag.

    python tools\\dump.py 04_sleep_10min [--full]

A csomagok végéről a nullákat levágja, hacsak nincs --full.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSHARK = r"C:\Program Files\Wireshark\tshark.exe"


def packets(name):
    """(idő, irány, adat) hármasok. A választ a tshark nem bontja mezőkre, ezért
    a nyers keretből vesszük: USBPcap-fejléc, kérésnél utána 8 bájt setup."""
    out = subprocess.run(
        [TSHARK, "-r", str(ROOT / "captures" / f"{name}.pcapng"), "-Y",
         "usb.transfer_type == 2 && usb.data_len > 0 && (usbhid.setup.bRequest == 9 || usb.src != \"host\")",
         "-T", "json", "-x"],
        capture_output=True, text=True, encoding="utf-8",
    ).stdout
    for frame in json.loads(out or "[]"):
        layers = frame["_source"]["layers"]
        raw = bytes.fromhex(layers["frame_raw"][0])
        header_len = int.from_bytes(raw[:2], "little")
        is_request = layers["usb"]["usb.src"] == "host"
        data = raw[header_len + (8 if is_request else 0):]
        yield float(layers["frame"]["frame.time_relative"]), ("küldés" if is_request else "válasz"), data


def main():
    name = sys.argv[1]
    full = "--full" in sys.argv
    for t, direction, data in packets(name):
        shown = data if full else data.rstrip(b"\x00")
        print(f"{t:.2f} mp, {direction}, {len(data)} bájt: {shown.hex(' ')}")


if __name__ == "__main__":
    main()
