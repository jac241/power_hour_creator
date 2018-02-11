# Power Hour Creator

[Download for Windows and macOS](https://github.com/jac241/power_hour_creator/releases)

![power hour creator screenshot](https://user-images.githubusercontent.com/3792672/36080093-cfd000ae-0f58-11e8-9532-4eed0644cd3d.PNG)

Easily create video or audio power hours from YouTube videos. Add your urls, pick start times, add an intermission with the full song option, and create your power hour.

Power Hour Creator automatically downloads the videos, cuts them to 60 seconds, and merges them into one file for you. Use the import and export options to share the power hour tracklists.

## Development
Uses Python 3.6, PyQt 5, [youtube-dl](https://github.com/rg3/youtube-dl), ffmpeg, and [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize).

## Building
To build:
```
pyinstaller power_hour_creator.spec
```

### Windows
https://github.com/pyinstaller/pyinstaller/issues/1566
Building on Windows 10 with pyinstaller requires Windows 10 Universal C Runtime found here: https://www.microsoft.com/en-us/download/details.aspx?id=48234

### macOS
Building on macOS using python installed from pyenv requires a special environment variable when building python. Instructions here: https://github.com/pyenv/pyenv/issues/443



## License

Power Hour Creator is released under the [GPLv3 License](https://opensource.org/licenses/GPL-3.0).
