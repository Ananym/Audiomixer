<div style="display: flex; align-items: center;">
  <img src="./icon.png" alt="Quick Audio Mixer Icon" style="width: 50px; height: 50px; margin-right: 10px; margin-bottom: 20px;">
  <h1>Quick Audio Mixer</h1>
</div>

Adds volume mixing hotkeys to windows, allowing you to quickly adjust volume on programs without a long trip through windows volume mixer.
Supports both keyboard keys and scrolling to adjust volume, with configurable hotkeys.
Available as a pyinstaller-packaged executable - see releases.

## Release Usage

Warning: even uncompressed, the release archive is currently not very antivirus friendly due to the system calls.
You may find it preferable to run from source.

Run the executable, or add it to startup using the included script.

## Default keys

| Binding | Effect |
|---------|--------|
| Ctrl + Shift + Scroll | Adjust volume of the window under the cursor |
| Ctrl + Shift + Middle click | Toggle mute on the window under the cursor |
| Ctrl + Shift + [ or ] | Adjust volume of the active window |
| Ctrl + Shift + m | Toggle mute on the active window |
| Ctrl + Shift + x | Quit the application |

You can also refresh the config or quit the application using the tray icon.

## Config

Modify the scale values in config to change increments volume is adjusted by.
Reassigning activators and function keys ought to work how you expect.

"searchChildrenOfParents" will also check for sibling processes when searching for audio sessions, which may be necessary for controlling some applications.
"searchMaxDepth" determines the extent to which Audiomixer traverses the process tree when looking for a related audio session.

## Todo

The various session-finding mechanisms in system_interactions evolved to handle an increasing set of edge cases, and is now somewhat unholy.  These bits could use some work to improve search performance.

Hoping to find a way to reduce the suspicion of antivirus software.

Feedback welcome!
