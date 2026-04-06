# FRLGSwitchSeedFarmer
Python script for farming FRLG Initial Seeds on CFWed Switch

## Prerequisites
- CFWed Switch
- [sys-botbase](https://github.com/olliz0r/sys-botbase?tab=readme-ov-file#installation) for WiFi setup or [sys-botbase-cpp](https://github.com/PokemonAutomation/sys-botbase-cpp?tab=readme-ov-file#installation) for USB setup, installed on the Switch
- [Hekate-Toolbox](https://github.com/WerWolv/Hekate-Toolbox/releases) installed on the Switch

## Recommended setup according to reliability
<ins>**Be sure to have your Switch charging so it doesn't die or suffer reduced performance**</ins>
- (Best) SysNAND + sys-botbase-cpp + Switch USB connected to the PC
- (Best) SysNAND + sys-botbase + Switch and PC both connected to the same router via Ethernet cable
- (Good) SysNAND + sys-botbase + PC connected to the same router via Ethernet cable and Switch WiFi connected
- (Medium) emuNAND + sys-botbase-cpp + Switch USB connected to the PC
- (Medium) emuNAND + sys-botbase + Switch and PC both connected to the same router via Ethernet cable
- (Bad) all other setups

## Setup Hekate-Toolbox
1) Download [this](https://downgit.github.io/#/home?url=https://github.com/Real96/FRLGSwitchSeedFarmer/blob/main/toolbox.json) zip file
2) Extract it and copy its content into the `/atmosphere/contents/430000000000000B/` folder on the Switch SD card

## Start sys-botbase / sys-botbase-cpp
1) Boot Atmosphere on your Swich
2) Open the Homebrew menu
3) Run Hekate-Toolbox
4) Turn on sys-botbase / sys-botbase-cpp

## How to run the script using Python
1) Install [Python](https://www.python.org/downloads/) (be sure to add it to `PATH` during the installation)
2) Open the terminal inside the folder of this project
3) Run `pip install -r requirements.txt` to install all the needed dependencies
4) Run `python main.py`

## How to run the script without using Python
1) Download the [latest release](https://github.com/Real96/FRLGSwitchSeedFarmer/releases/tag/latest-commit) of the executable
2) Run it

## How to find the Switch USB port and USB hub numbers
### Linux
Run the following command in the terminal:

`echo; for d in /sys/bus/usb/devices/*; do [[ -f $d/idVendor && -f $d/idProduct ]] || continue; [[ $(cat $d/idVendor) == "057e" && $(cat $d/idProduct) == "3000" ]] || continue; p=${d##*/}; p=${p#*-}; [[ $p == *.* ]] && echo "USB_PORT: ${p##*.} - USB_HUB: ${p%%.*}" || echo "USB_PORT: $p - USB_HUB: null"; done; echo`

### Windows
1) Right click on Windows logo (down-left) > `Device Manager`
2) Go to `libusbK USB Devices` > `Nintendo Switch`
3) Right click > `Properties`
4) In the `Location` field, you will see a text like the following one: `Port_#0004.Hub_#0001`
5) Pick the numbers after the zeros (`USB_PORT` is `4` and `USB_HUB` is `1` in this case)

## Usage:
1) Set up one of the environments described above ([**Recommended setup according to reliability**](https://github.com/Real96/FRLGSwitchSeedFarmer?tab=readme-ov-file#recommended-setup-according-to-reliability))
2) Start sys-botbase / sys-botbase-cpp on your Switch from Hekate-Toolbox (inside the Homebrew menu)
3) Edit the necessary settings of the `config.json` file, which is inside the folder of this project
4) Start Pokémon FireRed or Pokémon LeafGreen
5) Run the script choosing one of the two "**How to run**" methods described above

## Troubleshooting
- When you stop the script and you want to restart it, <ins>**ALWAYS**</ins> turn sys-botbase / sys-botbase-cpp off and back on from Hekate-Toolbox
- Be sure to disconnect all Joy-Con or controllers from the Switch to prevent drift from causing issues

## Settings
### IP
The IP address of your console (`System Settings` > `Internet` > `IP address`). Used only if `USB` setting is set to `false`.

### FIRST_SEED_TO_COLLECT
Used to specify where in a column to start farming seeds. A value of 0 will begin at the start of a column. A full column is should work out to < 2450 seeds.

### SEEDS_TO_COLLECT
Bot will run until this many seeds have been collected or it detects the title screen has looped. This number includes seed duplicates due to repeating the same frame. The recommended value with "AUTO" mode is 5500 for a full column run.

### SEED_BUTTON
The button that will be pressed and held on the title screen to get a seed. Must be one of ["A", "X", "L", "START", "PLUS"]. "START" is automatically remapped to "X". Note that "L" will be accepted, but will only work for you if your game is in L=A mode.

### REPEAT_MODE 
"AUTO" or "FIXED". "AUTO" will lead the program to dynamically choose how many times to repeat a given seed to resolve apparent timing issues. "FIXED" will repeat each seed a fixed number of times according to the value of REPEAT_TIMES.

### REPEAT_TIMES
If REPEAT_MODE is set to "FIXED", will repeat each seed attempt however many times this variable is set to. Ignored if REPEAT_MODE is set to "AUTO".

### OUTPUT_FILE_NAME_BASE
Prefix of the CSV file name in which raw results will be stored. It will be saved in the same folder of the script. Details about version, language, sound & LR button options, and the seed button will be automatically appended to it.

### PROCESSED_FILE_NAME_BASE
Prefix of the CSV file name in which processed results will be stored. Processed results compress duplicate seed entries and provides a time estimate. It will be saved in the same folder of the script. Details about version, language, sound & LR button options, and the seed button will be automatically appended to it. 

### PROCESSED_TIME_UNIT
Fraction of a GBA frame you want time estimates rounded to. A value of 2 would be rounding to the nearest half-frame.

### USB
Set this to `true` if you want to run the bot through USB ports (best option if you don't have an ethernet dongle for connecting the switch to the router). Set this to `false` if you want to run the bot though Internet (WiFi/Ethernet).

### USB_PORT
Number of the USB port of the Switch connected to the PC that will be attached to the bot. Used only if `USB` setting is set to `true`. To find the USB port number, use one the method described above according to your OS ([**How to find the Switch USB port**](https://github.com/Real96/FRLGSwitchSeedFarmer/tree/better_usb_binding?tab=readme-ov-file#how-to-find-the-switch-usb-hub-and-port-number)).

### USB_HUB
Number of the USB hub of the Switch connected to the PC that will be attached to the bot. Used only if `USB` setting is set to `true`. To find the USB hub number, use one of the methods described above according to your OS ([**How to find the Switch USB port and USB hub number**](https://github.com/Real96/FRLGSwitchSeedFarmer/tree/better_usb_binding?tab=readme-ov-file#how-to-find-the-switch-usb-port-and-hub-numbers)).

### SKIP_PROFILE_ENABLED
Set this to `true` when you have the option `Skip Selection Screen` (`Settings` > `Users`) turned on. The option appears only when your Switch has just one profile. This will avoid some unnecessary A presses.

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
