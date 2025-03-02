<div style="display: flex; align-items: center;">
  <img src="./icon.png" alt="Quick Audio Mixer Icon" style="width: 50px; height: 50px; margin-right: 10px; margin-bottom: 20px;">
  <h1>Quick Audio Mixer</h1>
</div>

Adds volume mixing hotkeys to windows, allowing you to quickly adjust volume on programs without a long trip through windows volume mixer.
Features:

- Configurable hotkeys to mute/adjust volume of window under cursor
- Configurable hotkeys to mute/adjust volume of active window
- Config via yaml file
- Tray icon
- Available as a pyinstaller-packaged executable

## Release Usage

Warning: some antiviruses may flag the installer package as malware due to the system calls. It may be preferable to run from source.
Download and extract the release package from https://github.com/Ananym/Audiomixer/releases .
Run the executable, or add it to startup using the included "add-exe-to-startup.ps1" script.

## Running from Source:

Requires python 3.10 or later.
Download the repository (git clone or download zip and extract)
Run `pip install -r requirements.txt` to install dependencies.
Run the included "add-py-to-startup.ps1" script to add audiomixer to startup,
Or just run `python audiomixer.py` to start the application directly.

## Default keys

| Binding                     | Effect                                       |
| --------------------------- | -------------------------------------------- |
| Ctrl + Shift + Scroll       | Adjust volume of the window under the cursor |
| Ctrl + Shift + Middle click | Toggle mute on the window under the cursor   |
| Ctrl + Shift + [ or ]       | Adjust volume of the active window           |
| Ctrl + Shift + m            | Toggle mute on the active window             |
| Ctrl + Shift + x            | Quit the application                         |

You can also refresh the config or quit the application using the tray icon.

## Config

Modify the scale values in config to change increments volume is adjusted by.
Reassigning activators and function keys ought to work how you expect.

"searchChildrenOfParents" will also check for sibling processes when searching for audio sessions, which may be necessary for controlling some applications.
"searchMaxDepth" determines the extent to which Audiomixer traverses the process tree when looking for a related audio session.

## Todo

The session-finding mechanisms in system_interactions grew convoluted to handle edge cases - needs tidying.
Hoping to find a way to reduce the suspicion of antivirus software besides buying an expensive codesign cert.

Feedback welcome!
