# FRLGSwitchSeedFarmer
Python script for farming FRLG Initial Seeds on CFWed Switch

## Usage:
1) Install [sys-botbase](https://github.com/olliz0r/sys-botbase?tab=readme-ov-file#installation) and start it
3) Edit all the settings inside the `config.json` file
4) Connect the Switch and the PC to the same WiFi/Ethernet connection
5) Start Pokémon FireRed or Pokémon LeafGreen
6) Start the script or the executable

## Settings
### IP
The IP address of your console (System Settings > Internet > IP address)

### A_PRESS_INITIAL_VALUE
Initial value for in game seed to start recording data at. Note that a value of 0 will still miss the first 1-2 seeds in a column due to the triggering condition. This may be improved in a future version.

### SEEDS_TO_COLLECT
Bot will run until this many seeds have been collected or it detects the title screen has looped. This number includes seed duplicates due to repeating the same frame. The recommended value with "AUTO" mode is 5500 for a full column run.

### REPEAT_MODE 
"AUTO" or "FIXED". "AUTO" will lead the program to dynamically choose how many times to repeat a given seed to resolve apparent timing issues. "FIXED" will repeat each seed a fixed number of times according to the value of REPEAT_TIMES.

### REPEAT_TIMES
If REPEAT_MODE is set to "FIXED", will repeat each seed attempt however many times this variable is set to. Ignored if REPEAT_MODE is set to "AUTO".

### OUTPUT_FILE_NAME
Name of CSV file in which raw results will be stored. It will be saved in the same folder of the script/executable.

### PROCESSED_FILE_NAME
Name of CSV file in which processed results will be stored. Processed results compress duplicate seed entries and provides a time estimate. Unit of time is 1/REAPEAT_TIMES GBA frames. It will be saved in the same folder of the script/executable.

### PROCESSED_TIME_UNIT
Fraction of a GBA frame you want time estimates rounded to. A value of 2 would be rounding to the nearest half-frame.

### DEBUG
Enable or disable debug printing.

## Credits:
* [olliz0r](https://github.com/olliz0r) for [sys-botbase](https://github.com/olliz0r/sys-botbase)
* [wwwwwwzx](https://github.com/wwwwwwzx) for [PyNXBot](https://github.com/wwwwwwzx/PyNXBot)
* [kwsch](https://github.com/kwsch) for [SysBot.NET](https://github.com/kwsch/SysBot.NET)
* [Lusamine](https://github.com/Lusamine) for [SySBot.NET fork](https://github.com/Lusamine/SysBot.NET/tree/moarencounterbots)
* [lincoln-lm](https://github.com/lincoln-lm) for the research and for [ten-lines](https://lincoln-lm.github.io/ten-lines)
* [Shao](https://github.com/c-poole) for the research and for improving the code
* [notblisy](https://github.com/notblisy) and [papajefe](https://github.com/papajefe) for the research
