"""Kapcsolat az AULA F75 konfigurációs csatornájával (HID feature report 6).

Csak a rögzítésekből már ismert konfigurációs parancsokat tartalmazza.
"""

import time

import hid

VID = 0x258A
PID = 0x010C
REPORT_ID = 0x06
REPORT_LEN = 520  # a report azonosítóval együtt
PAYLOAD_LEN = 512

CMD_IDENTIFY = 0x82
CMD_WRITE_KEYMAP = 0x03
CMD_READ_SETTINGS = 0x84
CMD_WRITE_SETTINGS = 0x04
CMD_WRITE_COLORS = 0x0A
CMD_WRITE_MACROS = 0x05

SETTINGS_LEN = 128  # a beállításblokk, a 8 bájtos fejléc után
MIN_GAP = 0.25  # másodperc két küldés között; a gyári program kb. 0,1-0,17 mp-et vár
BLOCK_END_MARK = b"\x5a\xa5"

# A beállításblokk ismert bájtjai (a blokkon belüli helyiérték)
SETTING_DEBOUNCE = 3  # pergésmentesítés: fokozat - 1 (1-5. fokozat = 0-4)
SETTING_TAP = 22  # a Tap réteg érzékenysége: 10-127, 0 = kikapcsolva
SETTING_SLEEP = 24  # alvási idő: perc * 2, 0 = kikapcsolva

LAYER_COUNT = 4  # Default, FN1, FN2, Tap
ENTRIES_PER_LAYER = 128
LAYER_END_MARK = bytes.fromhex("00005aa5")  # a 127. bejegyzés minden rétegben


class DeviceNotFound(Exception):
    pass


def find_config_path():
    """A 0xFF00 usage page-ű gyűjtemények közül az, amelyik 520 bájtos feature reportot fogad.

    Windows-on ez a Col06. A hidapi nem adja meg a feature report méretét, ezért
    a gyűjtemény nevére hagyatkozunk.
    """
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == 0xFF00 and b"Col06" in d["path"]:
            return d["path"]
    raise DeviceNotFound("Az AULA F75 konfigurációs csatornája nem található. Vezetékes módban van?")


class F75:
    def __init__(self):
        self.dev = hid.device()
        self.dev.open_path(find_config_path())
        self._last_send = 0.0

    def close(self):
        # Az utolsó írás feldolgozását is megvárjuk, mielőtt elengedjük az eszközt.
        wait = self._last_send + MIN_GAP - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self.dev.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    @staticmethod
    def _header(cmd, index, length):
        return bytes([cmd, index, 0x00, 0x01, 0x00]) + length.to_bytes(2, "little")

    def _send(self, header, payload=b""):
        # A billentyűzet az írásokat a saját tárolójába menti. Ha közben új parancs
        # érkezik, újraindulhat, ezért a gyári programnál kicsit lassabban küldünk.
        wait = self._last_send + MIN_GAP - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        report = bytes([REPORT_ID]) + header + payload
        report = report.ljust(REPORT_LEN, b"\x00")
        written = self.dev.send_feature_report(report)
        self._last_send = time.monotonic()
        if written < 0:
            raise IOError("A billentyűzet nem fogadta a csomagot.")

    def identify(self):
        """Azonosító-lekérdezés (0x82), ahogy a gyári program induláskor küldi."""
        self._send(self._header(CMD_IDENTIFY, 1, 6))
        time.sleep(0.02)
        return bytes(self.dev.get_feature_report(REPORT_ID, REPORT_LEN))

    def write_keymap(self, layers):
        """A négy réteg teljes kiosztásának írása, ugyanúgy, ahogy a gyári program menti.

        layers: négy darab 512 bájtos bájtsor, rétegenként 128 bejegyzés, egyenként 4 bájt.
        """
        if len(layers) != LAYER_COUNT or any(len(layer) != PAYLOAD_LEN for layer in layers):
            raise ValueError("Négy darab 512 bájtos réteg kell.")
        for index, layer in enumerate(layers):
            self._send(self._header(CMD_WRITE_KEYMAP, index, PAYLOAD_LEN), layer)

    def read_settings(self):
        """A 128 bájtos beállításblokk kiolvasása (0x84), ahogy a gyári program teszi."""
        header = self._header(CMD_READ_SETTINGS, 0, SETTINGS_LEN)
        self._send(header)
        time.sleep(0.02)
        reply = bytes(self.dev.get_feature_report(REPORT_ID, REPORT_LEN))
        block = reply[8:8 + SETTINGS_LEN]
        if reply[1:8] != header or len(block) != SETTINGS_LEN or block[-2:] != BLOCK_END_MARK:
            raise IOError("A billentyűzet válasza nem a várt formájú, nem írok semmit.")
        return bytearray(block)

    def write_settings(self, block):
        """A beállításblokk visszaírása (0x04). Csak kiolvasott, módosított blokkot írjunk vissza."""
        if len(block) != SETTINGS_LEN or bytes(block[-2:]) != BLOCK_END_MARK:
            raise ValueError("Hibás beállításblokk.")
        self._send(self._header(CMD_WRITE_SETTINGS, 0, SETTINGS_LEN), bytes(block))

    def write_macros(self, blob):
        """Az összes makró írása (0x05), egyetlen csomagban, ahogy a gyári program küldi."""
        if not 0 < len(blob) <= PAYLOAD_LEN:
            raise ValueError("A makróadat hossza 1 és 512 bájt között lehet.")
        self._send(self._header(CMD_WRITE_MACROS, 0, len(blob)), bytes(blob))

    def write_colors(self, table):
        """Az effektek színtáblájának írása (0x0a). A gyári program minden világítás-mentés után küldi."""
        if len(table) != PAYLOAD_LEN or bytes(table[506:508]) != BLOCK_END_MARK:
            raise ValueError("Hibás színtábla.")
        self._send(self._header(CMD_WRITE_COLORS, 0, PAYLOAD_LEN), bytes(table))
