@echo off
rem Builds the installer: PyInstaller, then Inno Setup.
rem Run from the project folder: packaging\build.cmd
setlocal
set PY=.venv\Scripts\python.exe
set OUT=build\dist
%PY% -m PyInstaller --noconfirm --clean --log-level WARN --distpath %OUT% --workpath build\work --specpath build ^
  --windowed --name "AULA F75 beallitasok" --paths . ^
  --add-data "%CD%\f75\data;f75\data" --collect-all accessible_output2 ^
  packaging\gui_main.py || exit /b 1
%PY% -m PyInstaller --noconfirm --clean --log-level WARN --distpath build\cli --workpath build\work-cli --specpath build ^
  --console --name f75 --paths . --add-data "%CD%\f75\data;f75\data" ^
  packaging\cli_main.py || exit /b 1
copy /y "build\cli\f75\f75.exe" "%OUT%\AULA F75 beallitasok\f75.exe" >nul || exit /b 1
set ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
"%ISCC%" /Q packaging\installer.iss || exit /b 1
echo Done: build\installer
