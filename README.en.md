# AULA F75 configurator

[Magyar változat](README.md)

An accessible replacement for the AULA F75 keyboard's vendor configuration software. It was made for a blind user and works well with screen readers (NVDA): the graphical interface uses native Windows controls, and the command-line version prints plain text only.

Features: key remapping on four layers (Default, FN1, FN2, Tap), macros, sleep time, debounce, tap/hold dual function, lighting, and saving and loading the configuration to and from a file. Unlike the vendor software, it handles the Hungarian ISO layout correctly.

The user interface is currently in Hungarian, and key names follow the Hungarian ISO layout. Where this document mentions interface labels, the Hungarian label is given with its English meaning.

## Warning

- This is not official AULA software, and the manufacturer does not support it. Use it at your own risk.
- It has only been tested with the Hungarian ISO AULA F75 (USB 258a:010c), firmware V11.0.4. It may not work with other versions or firmware.
- On other versions, especially the US ANSI one, it would probably swap the two keys to the right of the space bar, because it writes the Hungarian layout (AltGr and Fn there). Please do not use it yet with an ANSI or other non-Hungarian F75.
- The program only sends settings to the keyboard. It never writes firmware.
- Emergency: holding Fn and Esc for 3 seconds restores the keyboard to factory settings.

## Download and installation

The installer can be downloaded from the GitHub Releases page. It does not need administrator rights. Because it is not digitally signed, Windows SmartScreen may show a warning: choose "More info", then "Run anyway".

After installation, start the program from the Start menu ("AULA F75 beállítások"). If you ticked the option during installation, the `f75` command is available from any command prompt.

## Important notes

- The keyboard must be in wired mode, with the switch in the middle position.
- Do not run the vendor software at the same time as this program.
- Every time the vendor software saves, it writes the ANSI layout to the keyboard, which breaks the Hungarian layout: í, ű, AltGr and Fn end up in the wrong places. If you did use it, run `f75 apply` afterwards.

## The graphical interface

The window has three tabs; switch between them with Ctrl+Tab. After every change a short message appears at the bottom of the window, and NVDA reads it out automatically.

- **Gombkiosztás (Key assignment):** choose the layer in the Réteg (Layer) field (Alt+R). Below it, the Gombok (Keys) list (Alt+G) shows one key per row, with its function and whether it is factory default ("gyári") or changed ("átírva").
  - Enter: remap the key. In the dialog that opens, typing in the search field narrows the list of functions; you can also enter a key combination (for example ctrl+shift+esc), and for macros you can set how they repeat.
  - Delete: reset the key to factory default.
  - The Minden gyárira (Reset all) button resets the whole layout, after asking for confirmation.
- **Makrók (Macros):** the list of macros, with buttons for a new text macro, a new step macro, editing, deleting, and showing the steps. Macros are assigned to keys on the Gombkiosztás tab.
- **Beállítások (Settings):** sleep time, debounce, Tap, and lighting (on/off, effect, brightness, speed, colour). The Alkalmazás (Apply) button sends them to the keyboard; the Kiolvasás a billentyűzetből (Read from keyboard) button loads the current state.
- **Fájl (File) menu:** save to file (Ctrl+S), load from file (Ctrl+O), resend the key layout (Ctrl+R).

## Command-line use

With the installed version, the `f75` command works from anywhere. When running from source, run it in the project folder, with a `.\` prefix in PowerShell, for example `.\f75 show`. From source, the graphical interface starts with the `f75gui` command.

## Key layout

- `f75 remap capslock esc`: Caps Lock becomes Escape, on the Default layer.
- `f75 remap f1 mute --layer fn1`: Fn+F1 mutes. The layer can be default, fn1, fn2 or tap.
- `f75 remap capslock ctrl+shift+esc`: key combinations can be given with plus signs.
- `f75 remap capslock fn2`: Caps Lock becomes an FN2 key. Holding it activates the FN2 layer, which you can assign with `--layer fn2`. The keyboard has no FN2 key by default.
- `f75 remap capslock capslock --layer tap`: dual function. When Tap is turned on, a short press gives the Tap layer's function and holding gives the Default layer's. For example, together with `f75 remap capslock fn2`, Caps Lock is Caps Lock when tapped and an FN2 key when held. The tap function is only sent when the key is released.
- `f75 reset capslock`: reset one key to factory default. `--layer` works here too.
- `f75 reset`: reset the whole key layout to factory default, on all layers.
- `f75 show`: list the changed keys.
- `f75 show --all --layer fn1`: list all keys of a layer, one per line.
- `f75 keys`: the names of the keys and of the functions you can assign to them.
- `f75 apply`: resend the key layout recorded by the program.

Key names follow the Hungarian layout: `z` is the key that types Z in the Hungarian layout (the Y key on a US keyboard), `0` is the key to the left of 1, and accented letters have their own names. The two keys to the right of the space bar are `altgr` and `fn`; pressing the knob is `tekerő`.

The key layout cannot be read back from the keyboard, so the program keeps a record of your changes in `%APPDATA%\F75Konfig\allapot.json`.

## Macros

- `f75 macro text koszon "Best regards, User"`: a macro that types the text, following the Hungarian layout, with accents, capitals and common symbols (for example @, #, €).
- `f75 macro set masol ctrl+c 500ms ctrl+v`: a macro made of keys and combinations, separated by spaces. `500ms` is a pause.
- `f75 macro list`: the list of macros, and which keys they are on.
- `f75 macro show koszon`: the steps of a macro.
- `f75 macro delete koszon`: delete a macro. Only possible if it is not assigned to any key.
- `f75 remap j macro:koszon --layer fn1`: assign the macro to a key, here Fn+J.
  - `--repeat 3`: runs three times.
  - `--while-held`: repeats while you hold the key.
  - `--until-key`: repeats until you press another key.

All macros together can be at most 512 bytes, roughly 100 typed characters. Capitals and symbols take twice as much space as lowercase letters.

## Sleep, debounce, lighting

These are stored in the keyboard and can be read back.

- `f75 sleep`: show the sleep time. It only applies in wireless mode.
- `f75 sleep 10`: sleep time in minutes. Possible values: 1, 1.5, 2, 3, 4, 5, 10, 15, 20.
- `f75 sleep off`: turn sleep off.
- `f75 debounce`: show the debounce setting.
- `f75 debounce 3`: debounce level, from 1 to 5.
- `f75 tap`: show the Tap (dual function) setting.
- `f75 tap 40`: turn Tap on with a sensitivity from 10 to 127. The higher the number, the longer a press still counts as a tap. At 10, half a second already counts as holding; at 69, one second still counts as a tap.
- `f75 tap off`, `f75 tap on`: turn Tap off and on.
- `f75 light`: show the lighting settings.
- `f75 light effect neon`: choose an effect. Effects: off, fixed, respire, rainbow, flash_away, raindrops, ripples, stars, snake, neon, reaction, sine_wave, windmill, waterfall, blossoming, self_define.
- `f75 light brightness 5`: brightness, from 0 to 9.
- `f75 light speed 2`: speed, from 0 to 4.
- `f75 light color piros`: colour by Hungarian name (piros red, zöld green, kék blue, sárga yellow, lila purple, türkiz cyan, fehér white, narancs orange), as hexadecimal (for example ff8000), or `colourful` for multicolour mode.
- `f75 light off`, `f75 light on`: turn the lighting off and on.

Brightness, speed and colour always apply to the currently selected effect.

## Saving and loading

- `f75 save beallitasaim.json`: save all settings to a file.
- `f75 load beallitasaim.json`: load all settings from a file and send them to the keyboard.

## Running from source

Requires Python 3.14. In the project folder:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Project structure

- `f75`: the program itself.
- `tools`: the tools used to reverse engineer the protocol (USB capture, driving the vendor software, analysis).
- `research`: the description of the reverse-engineered protocol (`research\protokoll.md`, in Hungarian). For copyright reasons the vendor software's files are not in the repository; for development they can be copied from the vendor software's `Dev\kb` folder into `research\gyari`.
- `captures`: the USB captures. The capture tool filters out keystrokes.

## Building the installer

You need PyInstaller (`.venv\Scripts\python.exe -m pip install pyinstaller`) and Inno Setup 6 (`winget install JRSoftware.InnoSetup --scope user`). Then, in the project folder:

```
packaging\build.cmd
```

The result: `build\installer\AULA_F75_beallitasok_telepito_1.0.0.exe`.

## License

MIT, see the `LICENSE` file.
