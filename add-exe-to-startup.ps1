$exeName = "audiomixer.exe"
$currentDir = Get-Location
$exePath = Join-Path -Path $currentDir -ChildPath $exeName

if (-not (Test-Path $exePath)) {
    Write-Host "Error: The executable '$exeName' was not found in the current directory." -ForegroundColor Red
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

$shell = New-Object -ComObject WScript.Shell
$startupFolder = $shell.SpecialFolders.Item("Startup")
$shortcut = $shell.CreateShortcut("$startupFolder\$exeName.lnk")
$shortcut.TargetPath = $exePath
$shortcut.Save()

Write-Host "Success: $exeName has been added to Windows startup." -ForegroundColor Green
Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')