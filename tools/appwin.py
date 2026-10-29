"""A gyári program ablakának kezelése: indítás, ablakkép, kattintás.

    python tools\\appwin.py start            elindítja, ha nem fut
    python tools\\appwin.py shot kep.png     ablakkép (képernyőfüggöny mellett is)
    python tools\\appwin.py click X Y        kattintás az ablakon belüli X,Y pontra
    python tools\\appwin.py close            szabályos bezárás
    python tools\\appwin.py popup kep.png    a felugró ablak képe
    python tools\\appwin.py dialog SZÖVEG    felugró ablak: szöveg beírása és OK
"""

import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

OEMDRV = r"C:\Program Files (x86)\AULA\F75\OemDrv.exe"
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
user32.SetProcessDPIAware()
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.UINT]
user32.SetForegroundWindow.argtypes = [wt.HWND]
user32.GetForegroundWindow.restype = wt.HWND


def find_pids():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq OemDrv.exe", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    return [int(line.split('","')[1]) for line in out.splitlines() if line.startswith('"')]


def popup_window():
    """A legkisebb látható ablak, ha a főablakon kívül van ilyen (felugró menü, párbeszédablak)."""
    windows = visible_windows()
    return min(windows, key=lambda f: f[1] * f[2]) if len(windows) > 1 else None


def main_window():
    windows = visible_windows()
    return max(windows, key=lambda f: f[1] * f[2]) if windows else None


def visible_windows():
    pids = set(find_pids())
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(hwnd):
            r = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            found.append((hwnd, r.right - r.left, r.bottom - r.top, r.left, r.top))
        return True

    user32.EnumWindows(cb, 0)
    return [f for f in found if f[1] > 1 and f[2] > 1]


def shot(path, w=None):
    w = w or main_window()
    if not w:
        print("A gyári program ablaka nem található.")
        return 1
    hwnd, width, height, left, top = w
    hdc = user32.GetWindowDC(hwnd)
    mem = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, width, height)
    gdi32.SelectObject(mem, bmp)
    user32.PrintWindow(hwnd, mem, 2)  # PW_RENDERFULLCONTENT
    buf = ctypes.create_string_buffer(width * height * 4)
    bmi = (ctypes.c_uint32 * 10)(40, width, -height, 1 | (32 << 16), 0, 0, 0, 0, 0, 0)
    gdi32.GetDIBits(mem, bmp, 0, height, buf, bmi, 0)
    Image.frombuffer("RGB", (width, height), buf, "raw", "BGRX", 0, 1).save(path)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem)
    user32.ReleaseDC(hwnd, hdc)
    print(f"Ablakkép mentve: {path}, méret {width}x{height}, bal felső sarok {left},{top}.")
    return 0


def child_controls(hwnd):
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(child, _):
        r = wt.RECT()
        user32.GetWindowRect(child, ctypes.byref(r))
        name = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(child, name, 64)
        found.append((child, name.value, r.left, r.top, r.right - r.left))
        return True

    user32.EnumChildWindows(hwnd, cb, 0)
    return found


def dialog(text):
    """A felugró párbeszédablak szövegmezőjébe írja a szöveget, és megnyomja az OK gombot
    (a bal oldali széles gombot). Üzenetekkel, fókuszváltás nélkül."""
    w = popup_window()
    if not w:
        print("Nincs felugró ablak.")
        return 1
    controls = child_controls(w[0])
    edits = [c for c in controls if c[1] == "Edit"]
    buttons = sorted((c for c in controls if c[1] == "Button" and c[4] > 50), key=lambda c: c[2])
    if text is not None and edits:
        user32.SendMessageW(edits[0][0], 0x000C, 0, ctypes.c_wchar_p(text))  # WM_SETTEXT
    if not buttons:
        print("Nincs OK gomb.")
        return 1
    user32.SendMessageW(buttons[0][0], 0x00F5, 0, 0)  # BM_CLICK
    time.sleep(0.5)
    print(f"Párbeszédablak: szöveg {text!r}, OK megnyomva.")
    return 0


def press_key_in_popup(vk):
    """Valódi leütés a felugró ablak szövegmezőjébe: rákattint, leüti a billentyűt,
    majd visszaadja a fókuszt és az egeret. A gyári program billentyűmezője csak valódi
    leütést fogad el."""
    w = popup_window()
    edits = [c for c in child_controls(w[0]) if c[1] == "Edit"] if w else []
    if not edits:
        print("Nincs szövegmező a felugró ablakban.")
        return 1
    _, _, left, top, width = edits[0]
    prev_fg = user32.GetForegroundWindow()
    prev_pos = wt.POINT()
    user32.GetCursorPos(ctypes.byref(prev_pos))
    user32.SetCursorPos(left + width // 2, top + 10)
    time.sleep(0.15)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.2)
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk, 0, 0x0002, 0)  # KEYEVENTF_KEYUP
    time.sleep(0.2)
    user32.SetCursorPos(prev_pos.x, prev_pos.y)
    if prev_fg:
        user32.SetForegroundWindow(prev_fg)
    text = ctypes.create_unicode_buffer(100)
    user32.GetWindowTextW(edits[0][0], text, 100)
    print(f"Leütés: {vk:#04x}, a mező tartalma: {text.value!r}.")
    return 0


def click(x, y, count=1, keys=()):
    """Kattintás az ablakon belüli X,Y pontra. A keys virtuális billentyűkódjait a kattintás
    után, még a fókusz visszaadása előtt leüti (helyben szerkeszthető mezőkhöz)."""
    w = main_window()
    if not w:
        print("A gyári program ablaka nem található.")
        return 1
    hwnd, _, _, left, top = w
    # A program csak valódi egérkattintásra reagál. Az ablakot egy pillanatra
    # legfelülre hozzuk, kattintunk, majd az egeret és a fókuszt visszaadjuk.
    prev_fg = user32.GetForegroundWindow()
    prev_pos = wt.POINT()
    user32.GetCursorPos(ctypes.byref(prev_pos))
    flags = 0x0001 | 0x0002 | 0x0010  # SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, flags)  # HWND_TOPMOST
    user32.SetCursorPos(left + x, top + y)
    time.sleep(0.15)
    for _ in range(count):
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # bal gomb le
        time.sleep(0.05)
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # bal gomb fel
        time.sleep(0.05)
    time.sleep(0.15)
    for vk in keys:
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(vk, 0, 0x0002, 0)
        time.sleep(0.03)
    if keys:
        time.sleep(0.2)
    user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, flags)  # HWND_NOTOPMOST
    user32.SetCursorPos(prev_pos.x, prev_pos.y)
    if prev_fg and prev_fg != hwnd:
        user32.SetForegroundWindow(prev_fg)
    time.sleep(0.5)
    print(f"Kattintás: {x},{y}.")
    return 0


def main():
    cmd = sys.argv[1]
    if cmd == "start":
        if not find_pids():
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 4  # SW_SHOWNOACTIVATE: ne vegye el a fókuszt
            subprocess.Popen([OEMDRV], cwd=str(Path(OEMDRV).parent), startupinfo=si)
            time.sleep(10)
        print("A gyári program fut." if main_window() else "Nem sikerült elindítani.")
        return 0
    if cmd == "shot":
        return shot(sys.argv[2])
    if cmd == "key":
        return press_key_in_popup(int(sys.argv[2], 0))
    if cmd == "dialog":
        return dialog(sys.argv[2] if len(sys.argv) > 2 else None)
    if cmd == "popup":
        w = popup_window()
        if not w:
            print("Nincs felugró ablak.")
            return 1
        return shot(sys.argv[2], w)
    if cmd == "click":
        return click(int(sys.argv[2]), int(sys.argv[3]))
    if cmd == "dclick":
        # dclick X Y [SZÖVEG]: duplakattintás, majd a szöveg (számjegyek) begépelése és Enter
        typed = [ord(ch) for ch in sys.argv[4]] + [0x0D] if len(sys.argv) > 4 else []
        return click(int(sys.argv[2]), int(sys.argv[3]), count=2, keys=typed)
    if cmd == "close":
        for pid in find_pids():
            subprocess.run(["taskkill", "/PID", str(pid)], capture_output=True)
        time.sleep(3)
        print("A gyári program bezárult." if not find_pids() else "Még fut.")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
