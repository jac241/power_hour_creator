# Power Hour Creator
todo...

# Building
https://github.com/pyinstaller/pyinstaller/issues/1566
Building on Windows 10 with pyinstaller requires Windows 10 Universal C Runtime found here: https://www.microsoft.com/en-us/download/details.aspx?id=48234
Building on macOS using python installed from pyenv requires a special environment variable when building python

To build:
```
pyinstaller power_hour_creator.spec
```