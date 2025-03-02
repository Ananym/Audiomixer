$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScriptPath = Join-Path $scriptDir "audiomixer.py"

$pythonCommands = @(
    "pythonw.exe", 
    "python3.exe",
    "python.exe",
    "py.exe -3 -m pythonw"
)

$pythonCmd = $null
foreach ($cmd in $pythonCommands) {
    # check if command exists in PATH
    if (Get-Command $cmd.Split()[0] -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    Write-Host "Error: No Python installation found"
    Write-Host "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

$command = if ($pythonCmd -eq "py.exe -3 -m pythonw") {
    "py.exe -3 -m pythonw `"$pythonScriptPath`""
} else {
    "$pythonCmd `"$pythonScriptPath`""
}

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
    Write-Host "Startup shortcut created using $pythonCmd"
} else {
    Write-Host "Error creating shortcut"
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')