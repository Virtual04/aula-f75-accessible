"""USB-forgalom rögzítése az AULA F75-ről, képernyőolvasó-barát kimenettel.

Használat:
    python tools\\capture.py 01_alap_megnyitas

Elindítja a tshark-ot az USBPcap1 ponton, Enterre leállítja, majd a nyers
felvételből kiszűri a billentyűzet forgalmát, a leütések nélkül. Az eredmény
a captures mappában lesz: nev.pcapng. A nyers felvételt törli.
"""

import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path

TSHARK = r"C:\Program Files\Wireshark\tshark.exe"
CAPTURES = Path(__file__).resolve().parent.parent / "captures"


def tshark_lines(*args):
    out = subprocess.run([TSHARK, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [line for line in out.stdout.splitlines() if line.strip()]


def count(path, display_filter):
    return len(tshark_lines("-r", str(path), "-Y", display_filter, "-T", "fields", "-e", "frame.number"))


def find_address(path):
    """A billentyűzet USB-címe. Az USBPcap a felvétel elején minden eszköz leíróját
    lekéri, ebből a gyártó- és termékazonosító alapján megtalálható."""
    found = tshark_lines("-r", str(path), "-Y", "usb.idVendor == 0x258a && usb.idProduct == 0x010c",
                         "-T", "fields", "-e", "usb.device_address")
    return int(found[0]) if found else None


def main():
    parser = argparse.ArgumentParser(description="AULA F75 USB-rögzítés")
    parser.add_argument("name", help="a rögzítés neve, például 01_alap_megnyitas")
    parser.add_argument("--interface", default=r"\\.\USBPcap1")
    parser.add_argument("--address", type=int, help="a billentyűzet USB-címe; alapból a felvételből derül ki")
    parser.add_argument("--stop-file", help="Enter helyett ennek a fájlnak a megjelenésére áll le")
    args = parser.parse_args()

    CAPTURES.mkdir(exist_ok=True)
    raw = CAPTURES / f"{args.name}_nyers.pcapng"
    filtered = CAPTURES / f"{args.name}.pcapng"
    if filtered.exists() or raw.exists():
        print(f"Hiba: már van {args.name} nevű rögzítés. Adj másik nevet.")
        return 1

    proc = subprocess.Popen(
        [TSHARK, "-i", args.interface, "-q", "-w", str(raw)],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"A rögzítés elindult: {args.name}.", flush=True)
    if args.stop_file:
        stop = Path(args.stop_file)
        while not stop.exists():
            time.sleep(0.5)
        stop.unlink()
    else:
        print("Most végezd el a változtatást a gyári programban.")
        input("Ha kész, nyomj Entert a leállításhoz. ")

    proc.send_signal(signal.CTRL_BREAK_EVENT)
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    print("A rögzítés leállt.")

    if not raw.exists():
        print("Hiba: nem készült felvétel.")
        return 1

    address = args.address or find_address(raw)
    if address is None:
        print("Hiba: a felvételben nem található az AULA F75 (258a:010c).")
        return 1
    dev = f"usb.device_address == {address}"
    # A leütéseket (megszakításos bejövő forgalom) kihagyjuk, a nyers fájlt töröljük.
    keystrokes = "(usb.transfer_type == 1 && usb.endpoint_address.direction == 1)"
    tshark_lines("-r", str(raw), "-Y", f"{dev} && !{keystrokes}", "-w", str(filtered))
    raw.unlink()

    total = count(filtered, dev)
    control = count(filtered, f"{dev} && usb.transfer_type == 2")
    set_report = count(filtered, f"{dev} && usbhid.setup.bRequest == 9")
    get_report = count(filtered, f"{dev} && usbhid.setup.bRequest == 1")
    interrupt_out = count(filtered, f"{dev} && usb.transfer_type == 1 && usb.endpoint_address.direction == 0")

    print(f"Billentyűzet-csomagok összesen: {total}.")
    print(f"Vezérlőátvitelek: {control}.")
    print(f"Ebből SET_REPORT kérés (küldés a billentyűzetnek): {set_report}.")
    print(f"Ebből GET_REPORT kérés (olvasás a billentyűzetről): {get_report}.")
    print(f"Megszakításos küldés a billentyűzetnek: {interrupt_out}.")
    print(f"Mentve: {filtered}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
