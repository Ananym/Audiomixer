$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScriptPath = Join-Path $scriptDir "audiomixer.py"

$command = "$pythonwPath -3 -m pythonw `"$pythonScriptPath`""
$startupFolder = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupFolder "RunAudiomixer.lnk"

$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "cmd.exe"
$shortcut.Arguments = "/c $command"
$shortcut.Description = "Run Audiomixer at Startup"
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Save()

if($?) {
    Write-Host "Startup shortcut created"
} else {
    Write-Host "Error creating shortcut"
}