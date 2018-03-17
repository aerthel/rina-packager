# rina-packager
Unpacks and repacks data.bin packages inside Nintendo DS games such as Touch Detective 1

## Who should use this
The rina-packager script allows easy unpack&repackaging of the data.bin file found inside the Nintendo DS game "Touch Detective" rom. That file contains all the game's resource files packaged in a single one, alongside some metadata (in short: file count, offset and size of each resource).
This tool may be useful in translation or modification efforts of the mentioned game or other Nintendo DS games, assuming they feature this "data.bin" packaging style.

## How to use
1. Edit the basePath variable on the rina-packager.py script, which should point to the data.bin file's parent folder. Save the script.
1. Open a Python 3 console and load the script.
1. Now you have available two commands: unpack() and repack()
1. Type "unpack()" on the console to have the script open the data.bin and create a subfolder for each found game file resource.
1. Type "repack()" on the console to have the script create a new data.bin file (with a timestamp, it doesn't overwrite the original) using the contents of the subfolders created by unpack().

## Features
 - Unpack and Repack commands.
 - unpack() generates a file list, in CSV format.
 - repack() doesn't overwrite the original data.bin file.
 - Dynamic Offset calculation, allows repack() to handle files of any size.
 
## Where/How do I get the data.bin file?
Use Crystal Tile 2 to open the nds rom file. You can get a copy of the data.bin file or even inject one inside the rom with the same tool.

## Is this only for the NDS "Touch Detective 1" game?
Unknown at the moment, but it is possible that other games may be using this "whole game in a single file" packaging style. However, this script has only been tested with the Touch Detective's data.bin file.
 
## Why the name "rina"?
RINA is the Touch Detective script's actor ID for the main protagonist, Mackenzie. It is also her original name in the Japanese version of the game.

## Acknowledgements
This was implemented according the info provided by the following users, on [this romhacking.net forum thread](https://www.romhacking.net/forum/index.php?topic=15605.0)
  - FAST6191
  - Auryn
