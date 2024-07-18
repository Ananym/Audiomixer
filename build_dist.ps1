$latestTag = git describe --tags --abbrev=0
if (-not $latestTag) {
    Write-Host "No tags found"
    exit 1
}
$version = $latestTag -replace '^v', ''

pyinstaller audiomixer.py --windowed --hidden-import pynput.keyboard._win32 --hidden-import pynput.mouse._win32 --hidden-import pynput._util.win32 --icon .\trayicon.ico --noconfirm --add-data "./trayicon.ico;."
if(-not $?) {
    Write-Host "Failed to build"
    exit 1
}

Copy-Item config.yaml dist/audiomixer/
Copy-Item .\readme.md dist\audiomixer\readme.md
Copy-Item .\LICENCE dist\audiomixer\LICENCE
Copy-Item ".\add-exe-to-startup.ps1" ".\dist\audiomixer\add-exe-to-startup.ps1"

Remove-Item ./dist/release-*.zip -ErrorAction SilentlyContinue

$releaseFileName = "audiomixer-$version.zip"
Compress-Archive -Path ./dist/audiomixer -DestinationPath "./dist/$releaseFileName" -CompressionLevel Fastest -Force

# antiviruses hate the binary slightly less if it isn't actually compressed
# Unfortunately it's then far too big for github releases
# [System.IO.Compression.ZipFile]::CreateFromDirectory("./dist/audiomixer", "./dist/release.zip", [System.IO.Compression.CompressionLevel]::NoCompression, $true)
