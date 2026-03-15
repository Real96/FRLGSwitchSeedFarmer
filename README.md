# FRLGSwitchSeedFarmer
Python script for farming FRLG Initial Seeds on CFWed Switch

## Usage:
1) Edit all the settings inside the `config.json` file
2) Connect the Switch and the PC to the same WiFi/Ethernet connection
3) Start Pokémon FireRed or Pokémon LeafGreen
4) Stat the script

## Settings
### IP
The IP address of your console (System Settings > Internet > IP address)

### APressInitialValue
Initial value for in game frame to start recording data at. Minimum tested and working value is 1724.

### APressUpperLimit
Last value for in game frame to start recording data at. Maxmum tested and working value is 4158.

### seedsToCollect
Number of seeds you want to collect in this run (will either collect these, or until it reaches upper limit).

### repeatTimes
Sub-frame granualarity. Value 4 means we increment in quarter frame steps.

### outputFileName
Name of CSV file in which results will be stored. It will be saved in the same folder of the script.

## Credits:
* [olliz0r](https://github.com/olliz0r) for [sys-botbase](https://github.com/olliz0r/sys-botbase)
* [wwwwwwzx](https://github.com/wwwwwwzx) for [PyNXBot](https://github.com/wwwwwwzx/PyNXBot)
* [kwsch](https://github.com/kwsch) for [SysBot.NET](https://github.com/kwsch/SysBot.NET)
* [Lusamine](https://github.com/Lusamine) for [SySBot.NET fork](https://github.com/Lusamine/SysBot.NET/tree/moarencounterbots)
* [lincoln-lm](https://github.com/lincoln-lm) for the research and for [ten-lines](https://lincoln-lm.github.io/ten-lines)
* [Shao](https://github.com/c-poole) for the research and for improving the code
* [notblisy](https://github.com/notblisy) and [papajefe](https://github.com/papajefe) for the research
