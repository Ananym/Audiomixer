pyinstaller audiomixer.py --windowed --hidden-import pynput.keyboard._win32 --hidden-import pynput.mouse._win32 --hidden-import pynput._util.win32 --icon .\trayicon.ico --noconfirm --add-data "./trayicon.ico;."
if(-not $?) {
    Write-Host "Failed to build"
    exit 1
}

Copy-Item config.yaml dist/audiomixer/
Copy-Item .\readme.md dist\audiomixer\readme.md
Copy-Item .\LICENCE dist\audiomixer\LICENCE
Copy-Item ".\add-exe-to-startup.ps1" ".\dist\audiomixer\add-exe-to-startup.ps1"

Remove-Item ./dist/release.zip

# Compress-Archive -Path ./dist/audiomixer -DestinationPath ./dist/release.zip -CompressionLevel Fastest -Force
# antiviruses hate the binary slightly less if it isn't actually compressed
[System.IO.Compression.ZipFile]::CreateFromDirectory("./dist/audiomixer", "./dist/release.zip", [System.IO.Compression.CompressionLevel]::NoCompression, $true)
