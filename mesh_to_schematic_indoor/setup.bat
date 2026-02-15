@Echo off
Echo installing chocolatey
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
Echo installing python
choco install python3
Echo installing pip
choco install pip
Echo Please make sure you have installed Visual Studio C++ Build Tools before continuing
Echo https://visualstudio.microsoft.com/downloads/?q=build+tools
pause
python -m pip install -r "%~dp0settings\requirements.txt"
Echo downloading CloudCompare
mkdir %~dp0TMP_installation_files
powershell -Command "Invoke-WebRequest https://www.danielgm.net/cc/release/CloudCompare_v2.12.alpha_setup_x64.exe -OutFile "%~dp0TMP_installation_files\CloudCompare_setup.exe""
Echo installing CloudCompare
"%~dp0TMP_installation_files\CloudCompare_setup.exe"
Echo installation finished!
@RD /S /Q "%~dp0TMP_installation_files"
pause
