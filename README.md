# MicroPython files downloader

I wrote this tool mainly because I wanted to download binary files from me CANPico, it is based on a MicroPython OS and I couldn't find any tool that provides this feature.
Thonny works with textual files and cannot handle binary files at all.

This tool is very stright forward, it enumorates the available serial ports and check if there is a MicroPython at the end of the port, than it lists the files and ask which one would you like to fetch, than it downloads the file to the same directory the python script was called from.

I tested this code on windows machine but need to try it on the Linux ASAP, WSL is not supported because it doesn't support serial ports.

This is by no mean a reference code, it's barely a POC material.

use this tool by hitting:
`Python3 mp_get_files.py`
