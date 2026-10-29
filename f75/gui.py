"""AULA F75 konfigurátor, grafikus felület (wxPython, natív Windows-vezérlők).

Indítás: pythonw -m f75.gui
"""

import sys

import wx

from f75 import actions, config, keys, lighting, macros
from f75.device import F75, SETTING_DEBOUNCE, SETTING_TAP, DeviceNotFound
from f75.keymap import LAYER_NAMES

try:
    from accessible_output2.outputs.auto import Auto
    _speech = Auto()
except Exception:  # a felolvasás nélkül is működjön
    _speech = None

APP_TITLE = "AULA F75 beállítások"
LAYER_LABELS = {"default": "Alap réteg (Default)", "fn1": "FN1 réteg (Fn nyomva tartva)",
                "fn2": "FN2 réteg (FN2-gomb nyomva tartva)", "tap": "Tap réteg (rövid leütésre)"}
COLOR_LABELS = {"colourful": "Többszínű (Colourful)", **{n: n.capitalize() for n in lighting.COLOR_NAMES}}
EFFECT_LABELS = {
    "fixed": "Állandó", "respire": "Lélegző", "rainbow": "Szivárvány", "flash_away": "Felvillanó",
    "raindrops": "Esőcseppek", "ripples": "Hullámok", "stars": "Csillagok", "snake": "Kígyó",
    "neon": "Neon", "reaction": "Leütésre reagáló", "sine_wave": "Szinuszhullám",
    "windmill": "Szélmalom", "waterfall": "Vízesés", "blossoming": "Virágzás",
    "self_define": "Egyéni (Self-define)",
}
REPEAT_CHOICES = ["Egyszer", "Megadott számszor", "Amíg nyomva tartod", "A következő leütésig"]

ERRORS = (DeviceNotFound, keys.UnknownKey, ValueError, OSError)


def show_error(parent, error):
    wx.MessageBox(str(error), "Hiba", wx.OK | wx.ICON_ERROR, parent)


def labelled(parent, sizer, text, control):
    """Címke és vezérlő egymás mellett. A címke a vezérlő előtt jön létre,
    így a képernyőolvasó a vezérlő nevének olvassa."""
    row = wx.BoxSizer(wx.HORIZONTAL)
    row.Add(wx.StaticText(parent, label=text), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
    row.Add(control, 1, wx.EXPAND)
    sizer.Add(row, 0, wx.EXPAND | wx.ALL, 6)
    return control


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title=APP_TITLE, size=(760, 560))
        self.cfg = config.load_state()
        self.CreateStatusBar()

        file_menu = wx.Menu()
        save_item = file_menu.Append(wx.ID_SAVE, "&Mentés fájlba...\tCtrl+S")
        load_item = file_menu.Append(wx.ID_OPEN, "&Betöltés fájlból...\tCtrl+O")
        apply_item = file_menu.Append(wx.ID_ANY, "Gombkiosztás &újraküldése\tCtrl+R")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "&Kilépés")
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&Névjegy")
        menubar = wx.MenuBar()
        menubar.Append(file_menu, "&Fájl")
        menubar.Append(help_menu, "&Súgó")
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_save, save_item)
        self.Bind(wx.EVT_MENU, self.on_load, load_item)
        self.Bind(wx.EVT_MENU, self.on_apply, apply_item)
        self.Bind(wx.EVT_MENU, lambda e: self.Close(), exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

        self.notebook = wx.Notebook(self)
        self.keymap_page = KeymapPage(self.notebook, self)
        self.macro_page = MacroPage(self.notebook, self)
        self.settings_page = SettingsPage(self.notebook, self)
        self.notebook.AddPage(self.keymap_page, "Gombkiosztás")
        self.notebook.AddPage(self.macro_page, "Makrók")
        self.notebook.AddPage(self.settings_page, "Beállítások")
        self.Centre()

    def announce(self, message):
        """Visszajelzés az állapotsorban, és felolvasás az NVDA-val, ha elérhető."""
        self.SetStatusText(message)
        if _speech:
            try:
                _speech.output(message)
            except Exception:
                pass

    def commit(self, message):
        """A gombkiosztás és a makrók elküldése, a nyilvántartás mentése."""
        with wx.BusyCursor():
            actions.commit(self.cfg)
        self.announce(message)

    def refresh_all(self):
        self.keymap_page.refresh()
        self.macro_page.refresh()

    def on_save(self, event):
        with wx.FileDialog(self, "Mentés fájlba", wildcard="Beállítások (*.json)|*.json",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = dialog.GetPath()
        cfg = dict(self.cfg)
        try:
            with wx.BusyCursor(), F75() as kb:
                cfg.update(actions.read_settings(kb, cfg))
                cfg["colors"] = config.color_table(cfg).hex()
        except ERRORS:
            self.announce("A billentyűzet nem érhető el, a beállításokat a nyilvántartásból mentem.")
        try:
            config.write(cfg, path)
        except ERRORS as e:
            show_error(self, e)
            return
        self.announce(f"Elmentve: {path}")

    def on_load(self, event):
        with wx.FileDialog(self, "Betöltés fájlból", wildcard="Beállítások (*.json)|*.json",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = dialog.GetPath()
        try:
            cfg = config.read(path)
            with wx.BusyCursor():
                actions.send(cfg, with_settings=True)
            config.save_state(cfg)
        except ERRORS as e:
            show_error(self, e)
            return
        self.cfg = cfg
        self.refresh_all()
        self.settings_page.load_from_keyboard()
        self.announce(f"Betöltve és elküldve: {path}")

    def on_apply(self, event):
        try:
            self.commit("A nyilvántartott gombkiosztás elküldve a billentyűzetre.")
        except ERRORS as e:
            show_error(self, e)

    def on_about(self, event):
        wx.MessageBox("AULA F75 beállítóprogram, akadálymentes változat.\n"
                      "A gyári program helyett, NVDA-val használható.", "Névjegy", wx.OK, self)


class KeymapPage(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.layer = labelled(self, sizer, "&Réteg:", wx.Choice(self, choices=list(LAYER_LABELS.values())))
        self.layer.SetSelection(0)
        sizer.Add(wx.StaticText(self, label="&Gombok (Enter: átírás, Delete: gyárira):"), 0, wx.LEFT | wx.TOP, 6)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, "Gomb", width=180)
        self.list.InsertColumn(1, "Funkció", width=340)
        self.list.InsertColumn(2, "Állapot", width=100)
        sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 6)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        remap = wx.Button(self, label="&Átírás...")
        reset = wx.Button(self, label="Gyá&rira")
        reset_all = wx.Button(self, label="&Minden gyárira...")
        for b in (remap, reset, reset_all):
            buttons.Add(b, 0, wx.RIGHT, 6)
        sizer.Add(buttons, 0, wx.ALL, 6)
        self.SetSizer(sizer)

        self.layer.Bind(wx.EVT_CHOICE, lambda e: self.refresh())
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda e: self.on_remap())
        self.list.Bind(wx.EVT_KEY_DOWN, self.on_key)
        remap.Bind(wx.EVT_BUTTON, lambda e: self.on_remap())
        reset.Bind(wx.EVT_BUTTON, lambda e: self.on_reset())
        reset_all.Bind(wx.EVT_BUTTON, lambda e: self.on_reset_all())
        self.refresh()

    @property
    def layer_name(self):
        return config.EDITABLE_LAYERS[self.layer.GetSelection()]

    def refresh(self):
        selected = max(self.list.GetFirstSelected(), 0)
        cfg = self.frame.cfg
        table = config.build_layers(cfg)[LAYER_NAMES.index(self.layer_name)]
        self.list.DeleteAllItems()
        self.keys = list(keys.PHYSICAL)
        for row, key in enumerate(self.keys):
            target = cfg["keymap"][self.layer_name].get(key)
            if target:
                function, state = self.describe(target), "átírva"
            else:
                i = keys.PHYSICAL[key]
                function, state = keys.decode(table[i * 4:i * 4 + 4]), "gyári"
                if not function.startswith("nyers"):
                    function = keys.label(function)
            self.list.InsertItem(row, keys.label(key))
            self.list.SetItem(row, 1, function)
            self.list.SetItem(row, 2, state)
        if self.keys:
            self.list.Select(min(selected, len(self.keys) - 1))
            self.list.Focus(min(selected, len(self.keys) - 1))

    def current_key(self):
        row = self.list.GetFirstSelected()
        return self.keys[row] if row >= 0 else None

    def on_key(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            self.on_reset()
        else:
            event.Skip()

    def on_remap(self):
        key = self.current_key()
        if not key:
            return
        with RemapDialog(self, self.frame.cfg, key, self.layer_name) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            target = dialog.target
        cfg = self.frame.cfg
        old = cfg["keymap"][self.layer_name].get(key)
        try:
            config.encode_target(cfg, target)
            cfg["keymap"][self.layer_name][key] = target
            self.frame.commit(f"Kész: {keys.label(key)} mostantól: {self.describe(target)}.")
        except ERRORS as e:
            self.restore(key, old)
            show_error(self, e)
        self.refresh()
        self.frame.macro_page.refresh()

    def describe(self, target):
        text = config.describe_target(target)
        return text if macros.parse_target(target) else keys.label(text)

    def restore(self, key, old):
        mapping = self.frame.cfg["keymap"][self.layer_name]
        if old is None:
            mapping.pop(key, None)
        else:
            mapping[key] = old

    def on_reset(self):
        key = self.current_key()
        if not key:
            return
        old = self.frame.cfg["keymap"][self.layer_name].pop(key, None)
        if old is None:
            self.frame.announce(f"{keys.label(key)} már eddig is gyári volt.")
            return
        try:
            self.frame.commit(f"Kész: {keys.label(key)} visszaállt a gyárira.")
        except ERRORS as e:
            self.restore(key, old)
            show_error(self, e)
        self.refresh()
        self.frame.macro_page.refresh()

    def on_reset_all(self):
        answer = wx.MessageBox("Minden gomb visszaálljon a gyárira, mind a négy rétegen? "
                               "A makrók megmaradnak, de egyik gombon sem lesznek rajta.",
                               "Minden gyárira", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self)
        if answer != wx.YES:
            return
        old = self.frame.cfg["keymap"]
        self.frame.cfg["keymap"] = config.empty()["keymap"]
        try:
            self.frame.commit("A teljes gombkiosztás visszaállt a gyárira.")
        except ERRORS as e:
            self.frame.cfg["keymap"] = old
            show_error(self, e)
        self.refresh()
        self.frame.macro_page.refresh()


class RemapDialog(wx.Dialog):
    """Funkció választása egy gombhoz: kereshető lista, kombináció vagy makró."""

    def __init__(self, parent, cfg, key, layer):
        super().__init__(parent, title=f"{keys.label(key)} átírása, {LAYER_LABELS[layer]}")
        self.items = [(f"{label}, {group}", name) for group, label, name in keys.target_catalog()]
        self.items += [(f"{name}, makró", f"macro:{name}") for name in cfg["macros"]]
        self.target = None

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.search = labelled(self, sizer, "&Keresés:", wx.TextCtrl(self))
        sizer.Add(wx.StaticText(self, label="&Funkciók:"), 0, wx.LEFT, 6)
        self.choices = wx.ListBox(self, size=(420, 260))
        sizer.Add(self.choices, 1, wx.EXPAND | wx.ALL, 6)
        self.combo = labelled(self, sizer, "Vagy &kombináció (például ctrl+shift+esc):", wx.TextCtrl(self))
        self.repeat = wx.RadioBox(self, label="Makró ismétlése", choices=REPEAT_CHOICES,
                                  majorDimension=1, style=wx.RA_SPECIFY_COLS)
        sizer.Add(self.repeat, 0, wx.EXPAND | wx.ALL, 6)
        self.count = labelled(self, sizer, "Ismétlés&szám:", wx.SpinCtrl(self, min=2, max=255, initial=2))
        sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.ALL, 6)
        self.SetSizerAndFit(sizer)

        self.search.Bind(wx.EVT_TEXT, lambda e: self.fill())
        self.choices.Bind(wx.EVT_LISTBOX, lambda e: self.update_macro_controls())
        self.choices.Bind(wx.EVT_LISTBOX_DCLICK, lambda e: self.on_ok(None))
        self.repeat.Bind(wx.EVT_RADIOBOX, lambda e: self.update_macro_controls())
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.fill()
        self.search.SetFocus()

    def fill(self):
        text = self.search.GetValue().lower()
        self.shown = [(label, name) for label, name in self.items if text in label.lower() or text in name]
        self.choices.Set([label for label, _ in self.shown])
        if self.shown:
            self.choices.SetSelection(0)
        self.update_macro_controls()

    def selected_name(self):
        i = self.choices.GetSelection()
        return self.shown[i][1] if i != wx.NOT_FOUND else None

    def update_macro_controls(self):
        name = self.selected_name()
        is_macro = bool(name and name.startswith("macro:")) and not self.combo.GetValue().strip()
        self.repeat.Enable(is_macro)
        self.count.Enable(is_macro and self.repeat.GetSelection() == 1)

    def on_ok(self, event):
        combo = self.combo.GetValue().strip().lower()
        if combo:
            target = combo
        else:
            target = self.selected_name()
            if not target:
                wx.MessageBox("Válassz funkciót a listából, vagy írj be egy kombinációt.", "Hiba",
                              wx.OK | wx.ICON_ERROR, self)
                return
            if target.startswith("macro:"):
                target += ["", f":{self.count.GetValue()}", ":held", ":untilkey"][self.repeat.GetSelection()]
        try:
            if not target.startswith("macro:"):
                keys.encode(target)
        except ERRORS as e:
            show_error(self, e)
            return
        self.target = target
        self.EndModal(wx.ID_OK)


class MacroPage(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="&Makrók:"), 0, wx.LEFT | wx.TOP, 6)
        self.list = wx.ListBox(self)
        sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 6)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        new_text = wx.Button(self, label="Új &szövegmakró...")
        new_steps = wx.Button(self, label="Új &lépésmakró...")
        edit = wx.Button(self, label="Sz&erkesztés...")
        delete = wx.Button(self, label="&Törlés")
        show = wx.Button(self, label="Lépések &megjelenítése")
        for b in (new_text, new_steps, edit, delete, show):
            buttons.Add(b, 0, wx.RIGHT, 6)
        sizer.Add(buttons, 0, wx.ALL, 6)
        sizer.Add(wx.StaticText(self, label="Gombra tenni a Gombkiosztás fülön lehet. "
                                            "Az összes makró együtt kb. 100 begépelt karakter lehet."), 0, wx.ALL, 6)
        self.SetSizer(sizer)
        new_text.Bind(wx.EVT_BUTTON, lambda e: self.edit(None, "text"))
        new_steps.Bind(wx.EVT_BUTTON, lambda e: self.edit(None, "steps"))
        edit.Bind(wx.EVT_BUTTON, lambda e: self.on_edit())
        self.list.Bind(wx.EVT_LISTBOX_DCLICK, lambda e: self.on_edit())
        delete.Bind(wx.EVT_BUTTON, lambda e: self.on_delete())
        show.Bind(wx.EVT_BUTTON, lambda e: self.on_show())
        self.refresh()

    def refresh(self):
        cfg = self.frame.cfg
        self.names = list(cfg["macros"])
        rows = []
        for name, macro in cfg["macros"].items():
            kind = f'szöveg: {macro["text"]}' if "text" in macro else f'lépések: {macro["steps"]}'
            users = ", ".join(f"{keys.label(k)} ({LAYER_LABELS[layer]})" for layer, k in config.macro_users(cfg, name))
            rows.append(f"{name}, {kind}, gombon: {users or 'nincs'}")
        self.list.Set(rows or ["Nincs makró"])
        if rows:
            self.list.SetSelection(0)

    def current(self):
        i = self.list.GetSelection()
        return self.names[i] if self.names and i != wx.NOT_FOUND else None

    def on_edit(self):
        name = self.current()
        if name:
            macro = self.frame.cfg["macros"][name]
            self.edit(name, "text" if "text" in macro else "steps")

    def edit(self, name, kind):
        cfg = self.frame.cfg
        with MacroDialog(self, cfg, name, kind) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            new_name, content = dialog.result
        old_macros = dict(cfg["macros"])
        old_keymap = {layer: dict(m) for layer, m in cfg["keymap"].items()}
        if name and new_name != name:
            # átnevezés: a sorrend és a gombokra tett hivatkozások maradjanak
            cfg["macros"] = {(new_name if n == name else n): m for n, m in cfg["macros"].items()}
            for mapping in cfg["keymap"].values():
                for k, t in mapping.items():
                    parsed = macros.parse_target(t)
                    if parsed and parsed[0] == name:
                        mapping[k] = f"macro:{new_name}" + t[len(f"macro:{name}"):]
        cfg["macros"][new_name] = {kind: content}
        try:
            config.validate(cfg)
            if config.macro_users(cfg, new_name):
                self.frame.commit(f"A {new_name} makró elmentve és elküldve a billentyűzetre.")
            else:
                config.save_state(cfg)
                self.frame.announce(f"A {new_name} makró elmentve. Gombra a Gombkiosztás fülön teheted.")
        except ERRORS as e:
            cfg["macros"], cfg["keymap"] = old_macros, old_keymap
            show_error(self, e)
        self.frame.refresh_all()

    def on_delete(self):
        name = self.current()
        if not name:
            return
        cfg = self.frame.cfg
        users = config.macro_users(cfg, name)
        if users:
            listed = ", ".join(keys.label(k) for _, k in users)
            wx.MessageBox(f"A makró gombon van: {listed}. Előbb állítsd vissza azt a gombot a Gombkiosztás fülön.",
                          "Nem törölhető", wx.OK | wx.ICON_INFORMATION, self)
            return
        if wx.MessageBox(f"Törlöd a {name} makrót?", "Törlés", wx.YES_NO | wx.NO_DEFAULT, self) != wx.YES:
            return
        del cfg["macros"][name]
        config.save_state(cfg)
        self.frame.announce(f"A {name} makró törölve.")
        self.frame.refresh_all()

    def on_show(self):
        name = self.current()
        if not name:
            return
        try:
            lines = macros.describe_events(macros.events_of(self.frame.cfg["macros"][name]))
        except ERRORS as e:
            show_error(self, e)
            return
        with TextDialog(self, f"A {name} makró lépései", "\n".join(lines)) as dialog:
            dialog.ShowModal()


class MacroDialog(wx.Dialog):
    def __init__(self, parent, cfg, name, kind):
        title = ("Szövegmakró" if kind == "text" else "Lépésmakró") + (" szerkesztése" if name else " létrehozása")
        super().__init__(parent, title=title)
        self.cfg, self.old_name, self.kind = cfg, name, kind
        self.result = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.name = labelled(self, sizer, "&Név:", wx.TextCtrl(self, value=name or ""))
        if kind == "text":
            text = "&Szöveg, amit begépel (Enter új sort jelent):"
            self.content = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(420, 120))
        else:
            text = "&Lépések szóközzel elválasztva, például: ctrl+c 500ms ctrl+v"
            self.content = wx.TextCtrl(self, size=(420, -1))
        if name:
            self.content.SetValue(cfg["macros"][name][kind])
        sizer.Add(wx.StaticText(self, label=text), 0, wx.LEFT | wx.TOP, 6)
        sizer.Add(self.content, 1, wx.EXPAND | wx.ALL, 6)
        sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.ALL, 6)
        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.name.SetFocus()

    def on_ok(self, event):
        name = self.name.GetValue().strip()
        content = self.content.GetValue().replace("\r\n", "\n")
        try:
            if not name or len(name) > macros.MAX_NAME:
                raise ValueError(f"A név 1-{macros.MAX_NAME} karakter lehet.")
            if name != self.old_name and name in self.cfg["macros"]:
                raise ValueError(f"Már van {name} nevű makró.")
            macros.events_of({self.kind: content})
        except ERRORS as e:
            show_error(self, e)
            return
        self.result = (name, content)
        self.EndModal(wx.ID_OK)


class TextDialog(wx.Dialog):
    """Hosszabb szöveg olvasása: csak olvasható, nyilakkal bejárható szövegmező."""

    def __init__(self, parent, title, text):
        super().__init__(parent, title=title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        control = wx.TextCtrl(self, value=text, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(420, 260))
        sizer.Add(control, 1, wx.EXPAND | wx.ALL, 6)
        sizer.Add(self.CreateButtonSizer(wx.OK), 0, wx.EXPAND | wx.ALL, 6)
        self.SetSizerAndFit(sizer)
        control.SetFocus()


class SettingsPage(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.current = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sleep = labelled(self, sizer, "&Alvási idő (csak vezeték nélküli módban):",
                              wx.Choice(self, choices=[actions.sleep_text(m) for m in config.SLEEP_MINUTES]))
        self.debounce = labelled(self, sizer, "&Pergésmentesítés fokozata:",
                                 wx.Choice(self, choices=[str(s) for s in config.DEBOUNCE_STAGES]))
        self.tap_on = wx.CheckBox(self, label="&Tap (kettős funkció) bekapcsolva")
        sizer.Add(self.tap_on, 0, wx.ALL, 6)
        self.tap = labelled(self, sizer, "Tap ér&zékenysége (10-127, nagyobb = hosszabb rövid leütés):",
                            wx.SpinCtrl(self, min=10, max=127, initial=69))
        self.light_on = wx.CheckBox(self, label="&Világítás bekapcsolva")
        sizer.Add(self.light_on, 0, wx.ALL, 6)
        self.effects = [e for e in lighting.EFFECTS if e != "off"]
        self.effect = labelled(self, sizer, "&Effekt:", wx.Choice(self, choices=[EFFECT_LABELS[e] for e in self.effects]))
        self.brightness = labelled(self, sizer, "&Fényerő (0-9):", wx.SpinCtrl(self, min=0, max=9, initial=9))
        self.speed = labelled(self, sizer, "&Sebesség (0-4):", wx.SpinCtrl(self, min=0, max=4, initial=4))
        self.colors = list(COLOR_LABELS)
        self.color = labelled(self, sizer, "S&zín:", wx.Choice(self, choices=list(COLOR_LABELS.values())))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        apply_button = wx.Button(self, label="Alkalma&zás")
        reload_button = wx.Button(self, label="Kiolvasás a &billentyűzetből")
        buttons.Add(apply_button, 0, wx.RIGHT, 6)
        buttons.Add(reload_button, 0)
        sizer.Add(buttons, 0, wx.ALL, 6)
        self.SetSizer(sizer)
        self.tap_on.Bind(wx.EVT_CHECKBOX, lambda e: self.update_enabled())
        self.light_on.Bind(wx.EVT_CHECKBOX, lambda e: self.update_enabled())
        apply_button.Bind(wx.EVT_BUTTON, lambda e: self.on_apply())
        reload_button.Bind(wx.EVT_BUTTON, lambda e: self.load_from_keyboard(announce=True))
        wx.CallAfter(self.load_from_keyboard)

    def update_enabled(self):
        self.tap.Enable(self.tap_on.GetValue())
        for control in (self.effect, self.brightness, self.speed, self.color):
            control.Enable(self.light_on.GetValue())

    def load_from_keyboard(self, announce=False):
        try:
            with wx.BusyCursor(), F75() as kb:
                self.current = actions.read_settings(kb, self.frame.cfg)
        except ERRORS as e:
            self.frame.announce(f"A billentyűzet nem érhető el: {e}")
            return
        s = self.current
        self.sleep.SetSelection(config.SLEEP_MINUTES.index(s["sleep"]) if s["sleep"] in config.SLEEP_MINUTES else 0)
        self.debounce.SetSelection(s["debounce"] - 1)
        self.tap_on.SetValue(s["tap"] != 0)
        self.tap.SetValue(s["tap"] or self.frame.cfg.get("tap") or 69)
        light = s["light"]
        self.light_on.SetValue(light["effect"] != "off")
        last = light if light["effect"] != "off" else {"effect": "neon", "brightness": 9, "speed": 4, "color": "colourful"}
        self.effect.SetSelection(self.effects.index(last["effect"]))
        self.brightness.SetValue(last["brightness"])
        self.speed.SetValue(last["speed"])
        color = last["color"]
        named = next((n for n, v in lighting.COLOR_NAMES.items() if v == color), color)
        if named not in self.colors:
            self.colors.append(named)
            self.color.Append(f"Egyéni ({named})")
        self.color.SetSelection(self.colors.index(named))
        self.update_enabled()
        if announce:
            self.frame.announce("A beállítások kiolvasva a billentyűzetből.")

    def on_apply(self):
        if self.current is None:
            self.load_from_keyboard()
            if self.current is None:
                return
        cfg, s = self.frame.cfg, self.current
        sleep = config.SLEEP_MINUTES[self.sleep.GetSelection()]
        debounce = self.debounce.GetSelection() + 1
        tap = self.tap.GetValue() if self.tap_on.GetValue() else 0
        try:
            with wx.BusyCursor(), F75() as kb:
                if sleep != s["sleep"]:
                    actions.set_sleep(kb, sleep)
                if debounce != s["debounce"]:
                    actions.set_setting(kb, SETTING_DEBOUNCE, debounce - 1)
                if tap != s["tap"]:
                    actions.set_setting(kb, SETTING_TAP, tap)
                if not self.light_on.GetValue():
                    if s["light"]["effect"] != "off":
                        actions.set_light(kb, cfg, effect="off")
                else:
                    color = self.colors[self.color.GetSelection()]
                    if color != "colourful":
                        color = lighting.parse_color(color).hex()
                    wanted = {"effect": self.effects[self.effect.GetSelection()],
                              "brightness": self.brightness.GetValue(), "speed": self.speed.GetValue(),
                              "color": color}
                    if wanted != s["light"]:
                        actions.set_light(kb, cfg, effect=wanted["effect"])
                        actions.set_light(kb, cfg, brightness=wanted["brightness"], speed=wanted["speed"],
                                          color=wanted["color"])
        except ERRORS as e:
            show_error(self, e)
            self.load_from_keyboard()
            return
        cfg.update({"sleep": sleep, "debounce": debounce, "tap": tap})
        config.save_state(cfg)
        self.load_from_keyboard()
        self.frame.announce("A beállítások elküldve a billentyűzetre.")


def main():
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
