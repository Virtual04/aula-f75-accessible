"""Makrók. A rögzítésekből kiderített formátum (05-ös parancs, egyetlen adatcsomag):

  fejléc: makrónként 2 bájt kezdőhely és 2 bájt hossz (kisebb helyiérték elöl)
  makrónként: 1 bájt névhossz, a név UTF-16LE kódolással, majd a lépések
  lépés, 4 bájt: jelző (00 lenyomás, 80 felengedés, +10 módosítóbillentyűnél),
                 várakozás ezredmásodpercben 2 bájton (nagyobb helyiérték elöl),
                 HID-billentyűkód

A gombon a bejegyzés: 03, mód, ismétlésszám, a makró sorszáma.
  mód: 01 = ismétlésszámszor, 02 = a következő leütésig, 04 = amíg nyomva tartod
"""

import re

from f75 import keys

TYPE_MACRO = 0x03
MODE_TIMES = 0x01
MODE_UNTIL_KEY = 0x02
MODE_WHILE_HELD = 0x04

FLAG_RELEASE = 0x80
FLAG_MODIFIER = 0x10
MAX_BLOB = 512  # nagyobb adatot még nem rögzítettünk, ezért nem is küldünk
MAX_NAME = 30
DEFAULT_DELAY = 20  # ms két lépés között
MAX_DELAY = 65535

MODIFIER_KEYCODES = {
    "lctrl": 0xE0, "lshift": 0xE1, "lalt": 0xE2, "lwin": 0xE3,
    "rctrl": 0xE4, "rshift": 0xE5, "altgr": 0xE6, "rwin": 0xE7,
}

# Szöveg -> (módosítók, billentyűnév) a magyar kiosztás szerint.
_SHIFTED = {"'": "1", '"': "2", "+": "3", "!": "4", "%": "5", "/": "6", "=": "7",
            "(": "8", ")": "9", "§": "0", "?": ",", ":": ".", "_": "-"}
_ALTGR = {"\\": "q", "|": "w", "€": "u", "[": "f", "]": "g", "$": "é", "<": "í",
          ">": "y", "#": "x", "&": "c", "@": "v", "{": "b", "}": "n", ";": ",", "*": "-"}
_PLAIN = {" ": "space", "\n": "enter", "\t": "tab"}


class MacroError(ValueError):
    pass


def char_to_combo(ch):
    if ch in _PLAIN:
        return [], _PLAIN[ch]
    if ch in _SHIFTED:
        return ["lshift"], _SHIFTED[ch]
    if ch in _ALTGR:
        return ["altgr"], _ALTGR[ch]
    if ch in keys.KEYCODES and len(ch) == 1:
        return [], ch
    lower = ch.lower()
    if lower != ch and lower in keys.KEYCODES and len(lower) == 1:
        return ["lshift"], lower
    raise MacroError(f"Ezt a karaktert nem tudom begépelni: {ch!r}")


def _event(key_code, release, delay):
    flags = (FLAG_RELEASE if release else 0) | (FLAG_MODIFIER if key_code >= 0xE0 else 0)
    return [flags, delay >> 8, delay & 0xFF, key_code]


def _combo_events(mods, key, delay):
    """Módosítók le, billentyű le-fel, módosítók fel (fordított sorrendben)."""
    events = [_event(MODIFIER_KEYCODES[m], False, delay) for m in mods]
    if key in MODIFIER_KEYCODES:
        events += [_event(MODIFIER_KEYCODES[key], False, delay), _event(MODIFIER_KEYCODES[key], True, delay)]
    else:
        events += [_event(keys.KEYCODES[key], False, delay), _event(keys.KEYCODES[key], True, delay)]
    events += [_event(MODIFIER_KEYCODES[m], True, delay) for m in reversed(mods)]
    return events


def _add_wait(events, ms):
    if not events:
        raise MacroError("A makró nem kezdődhet szünettel.")
    last = events[-1]
    total = min(((last[1] << 8) | last[2]) + ms, MAX_DELAY)
    last[1], last[2] = total >> 8, total & 0xFF


def parse_steps(text):
    """'ctrl+c 500ms ctrl+v' -> lépések listája."""
    events = []
    for token in text.lower().split():
        wait = re.fullmatch(r"(\d+)ms", token)
        if wait:
            _add_wait(events, int(wait.group(1)))
            continue
        *mods, key = token.split("+")
        mods = [keys.MODIFIER_ALIASES.get(m, m) for m in mods]
        key = keys.MODIFIER_ALIASES.get(key, key)
        for m in mods:
            if m not in MODIFIER_KEYCODES:
                raise MacroError(f"Ismeretlen módosító: {m}")
        if key not in keys.KEYCODES and key not in MODIFIER_KEYCODES:
            raise MacroError(f"Ismeretlen billentyű: {key}. A nevek listája: f75 keys")
        events += _combo_events(mods, key, DEFAULT_DELAY)
    if not events:
        raise MacroError("A makró üres.")
    return events


def parse_text(text):
    events = []
    for ch in text:
        mods, key = char_to_combo(ch)
        events += _combo_events(mods, key, DEFAULT_DELAY)
    if not events:
        raise MacroError("A szöveg üres.")
    return events


def events_of(macro):
    """A konfigurációban tárolt makró ({"text": ...} vagy {"steps": ...}) lépései."""
    if "text" in macro:
        return parse_text(macro["text"])
    return parse_steps(macro["steps"])


def describe_events(events):
    names = {code: name for name, code in keys.KEYCODES.items()}
    names.update({code: name for name, code in MODIFIER_KEYCODES.items()})
    lines = []
    for flags, hi, lo, code in events:
        action = "fel" if flags & FLAG_RELEASE else "le"
        lines.append(f"{names.get(code, hex(code))} {action}, várakozás {(hi << 8) | lo} ms")
    return lines


def build_blob(macros):
    """A makrók (név -> konfiguráció, a sorrend a sorszám) adatcsomagja."""
    records = []
    for name, macro in macros.items():
        encoded = name.encode("utf-16-le")
        events = events_of(macro)
        records.append(bytes([len(encoded)]) + encoded + bytes(b for e in events for b in e))
    header_len = 4 * len(records)
    header, offset = b"", header_len
    for record in records:
        header += offset.to_bytes(2, "little") + len(record).to_bytes(2, "little")
        offset += len(record)
    blob = header + b"".join(records)
    if len(blob) > MAX_BLOB:
        raise MacroError(f"A makrók együtt túl hosszúak ({len(blob)} bájt, legfeljebb {MAX_BLOB}). "
                         "Rövidítsd vagy törölj makrót.")
    return blob


def parse_target(target):
    """'macro:NEV[:3|:held|:untilkey]' -> (név, mód, ismétlésszám), vagy None, ha nem makró."""
    if not target.startswith("macro:"):
        return None
    name, _, option = target[len("macro:"):].partition(":")
    if option == "held":
        return name, MODE_WHILE_HELD, 1
    if option == "untilkey":
        return name, MODE_UNTIL_KEY, 1
    count = int(option) if option else 1
    if not 1 <= count <= 255:
        raise MacroError("Az ismétlésszám 1 és 255 között lehet.")
    return name, MODE_TIMES, count


def entry(target, macro_names):
    name, mode, count = parse_target(target)
    if name not in macro_names:
        raise MacroError(f"Nincs ilyen makró: {name}. A makrók listája: f75 macro list")
    return bytes([TYPE_MACRO, mode, count, macro_names.index(name)])


def describe_target(target):
    name, mode, count = parse_target(target)
    if mode == MODE_WHILE_HELD:
        return f"{name} makró, ismétlés amíg nyomva tartod"
    if mode == MODE_UNTIL_KEY:
        return f"{name} makró, ismétlés a következő leütésig"
    return f"{name} makró" + (f", {count}-szor" if count > 1 else "")
