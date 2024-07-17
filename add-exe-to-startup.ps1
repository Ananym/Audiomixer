
$exeName = "audiomixer.exe"
$currentDir = Get-Location
$exePath = Join-Path -Path $currentDir -ChildPath $exeName

if (-not (Test-Path $exePath)) {
    [System.Windows.Forms.MessageBox]::Show("The executable '$exeName' was not found in the current directory.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    exit
}

$shell = New-Object -ComObject WScript.Shell
$startupFolder = $shell.SpecialFolders.Item("Startup")
$shortcut = $shell.CreateShortcut("$startupFolder\$exeName.lnk")
$shortcut.TargetPath = $exePath
$shortcut.Save()

[System.Windows.Forms.MessageBox]::Show("$exeName has been added to Windows startup.", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)