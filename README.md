
# OBS WebSocket Client

This is a GUI client using OBS WebSocket. Used for controlling OBS remotely (e.g for using with capture cards on another computer).

The main purpose of this is for saving replays with a hotkey remotely, since I couldn't find any. There are still many missing features.

I have not tested on any OS except for Windows.

# Usage

- Download the executable from the [Releases](https://github.com/dng-nguyn/obs-ws-client/releases) page.

- Enable OBS WebSocket:

<image

- And connect to the remote OBS using the login details.

# Development

Requirements: `git`, `python3`,  `pip`, `PyInstaller`

## Building:

Clone the repository: 
```sh
git clone 
```

Install libraries: 
```sh
pip install -r requirements.txt
```

Build executable with PyInstaller:
```sh
python -m PyInstaller --onefile --noconsole main.py
```