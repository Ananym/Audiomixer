# Quick Audio Mixer

Adds volume mixing hotkeys to windows, allowing you to quickly mix noisy apps without an arduous trip through windows volume mixer.
Works with both keyboard keys and scrolling to adjust volume, with configurable hotkeys.
Available as a pyinstaller-packaged executable - see releases.

## Usage

Run the executable, or add it to startup.

Default keys:
Ctrl + Shift + Scroll while pointing at a noisy window to adjust its volume,
Ctrl + Shift + Middle click to toggle mute,
Ctrl + Shift + { or } to adjust volume of active window,
Ctrl + Shift + m to toggle mute on active window,
Ctrl + Shift + x to quit, or quit via tray icon.

## Config

Modify the scale values in config to change increments volume is adjusted by.
Reassigning activators and function keys ought to work how you expect.

"searchChildrenOfParents" will also check for sibling processes when searching for audio sessions, which may be necessary for controlling some applications.
"searchMaxDepth" determines the extent to which Audiomixer traverses the process tree when looking for a related audio session.

## Todo

The various session-finding mechanisms in system_interactions evolved to handle an increasing set of edge cases, and is now somewhat unholy.  These bits could use some work to improve search performance.

Feedback welcome!
