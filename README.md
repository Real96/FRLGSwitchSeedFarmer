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
The IP address of your console (System Settings > Internet > IP address). Used only if `USB` setting is set to `false`.

### A_PRESS_INITIAL_VALUE
Initial value for in game seed to start recording data at. A value of 0 will begin at the start of a column.

### SEEDS_TO_COLLECT
Bot will run until this many seeds have been collected or it detects the title screen has looped. This number includes seed duplicates due to repeating the same frame. The recommended value with "AUTO" mode is 5000 for a full column run.

### SEED_BUTTON
The button that will be pressed and held on the title screen to get a seed. Must be one of ["A", "X", "L", "START", "PLUS"]. "START" is automatically remapped to "X". Note that "L" will be accepted, but will only work for you if your game is in L=A mode.

### REPEAT_MODE 
"AUTO" or "FIXED". "AUTO" will lead the program to dynamically choose how many times to repeat a given seed to resolve apparent timing issues. "FIXED" will repeat each seed a fixed number of times according to the value of REPEAT_TIMES.

### REPEAT_TIMES
If REPEAT_MODE is set to "FIXED", will repeat each seed attempt however many times this variable is set to. Ignored if REPEAT_MODE is set to "AUTO".

### OUTPUT_FILE_NAME
Name of CSV file in which raw results will be stored. It will be saved in the same folder of the script/executable. Highly recommended that this contains details about version, language, sound & LR button options, and the seed button for your own sanity. 

### PROCESSED_FILE_NAME
Name of CSV file in which processed results will be stored. Processed results compress duplicate seed entries and provides a time estimate. It will be saved in the same folder of the script/executable. Highly recommended that this contains details about version, language, sound & LR button options, and the seed button for your own sanity. 

### PROCESSED_TIME_UNIT
Fraction of a GBA frame you want time estimates rounded to. A value of 2 would be rounding to the nearest half-frame.

### USB
Set this to `true` if you want to run the bot through USB ports (best option if you don't have an ethernet dongle for connecting the switch to the router). Set this to `false` if you want to run the bot though Internet (WiFi/Ethernet).

### USB_INDEX
Index of the Switch connected to the PC that will be attached to the bot. Used only if `USB` setting is set to `true`

### EMUNAND
Set this to `true` only if you are on EmuNand. This will handle slow games booting/closing timing.

### DEBUG
Set this to `true` to enable debug printing. Set this to `false` to disable it.

## Credits:
* [olliz0r](https://github.com/olliz0r) for [sys-botbase](https://github.com/olliz0r/sys-botbase)
* [Koi-3088](https://github.com/Koi-3088) for [sys-botbase-cpp](https://github.com/PokemonAutomation/sys-botbase-cpp)
* [wwwwwwzx](https://github.com/wwwwwwzx) for [PyNXBot](https://github.com/wwwwwwzx/PyNXBot)
* [kwsch](https://github.com/kwsch) for [SysBot.NET](https://github.com/kwsch/SysBot.NET)
* [Lusamine](https://github.com/Lusamine) for [SySBot.NET fork](https://github.com/Lusamine/SysBot.NET/tree/moarencounterbots)
* [lincoln-lm](https://github.com/lincoln-lm) for the research and for [ten-lines](https://lincoln-lm.github.io/ten-lines)
* [Shao](https://github.com/c-poole) for the research and for improving the code
* [notblisy](https://github.com/notblisy) and [papajefe](https://github.com/papajefe) for the research
