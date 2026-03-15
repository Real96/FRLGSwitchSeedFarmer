# Go to root/test of PyNXBot
import signal, json, csv, os
from time import time
from seed_bot import SeedBot

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

bot = SeedBot(config["IP"])
APressInitialValue = config["APressInitialValue"]
APressUpperLimit = config["APressUpperLimit"]
seedsToCollect = config["seedsToCollect"]
repeatTimes = config["repeatTimes"]
outputFileName = config["outputFileName"]


def signal_handler(_signal, _advances):  # CTRL+C handler
    print("Stop request")
    bot.close()


signal.signal(signal.SIGINT, signal_handler)

lowVBlankHeralding = 256
seedsCounter = 0
VBlankCounter = 0
repeatCounter = 0
tic = 0
toc = 0

APressValue = APressInitialValue
delay = 16.7427 / 1000 / repeatTimes
resetTime = time()
consecutiveFailures = 0

# Make file with header if file did not already exist
if not os.path.exists(outputFileName):
    with open(outputFileName, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Seed", "Frame", "Time"])

while (
    seedsCounter < seedsToCollect
    and APressValue <= APressUpperLimit
    and consecutiveFailures < 5
):
    try:
        VBlankCounter = bot.read_vblank_counter()
    except Exception as e:
        print("Error reading, resetting")
        bot.restart_game()
        bot.pause(1)
        resetTime = time()
        consecutiveFailures += 1
        continue

    # Check if we have not reached our "boot succeeded" detection within 5 seconds, reset if need be
    if tic == 0 and time() - resetTime > 10:
        # We failed to properly boot, try again
        print("Failed to boot")
        consecutiveFailures += 1
        bot.restart_game()
        bot.pause(1)
        resetTime = time()
        continue

    # Early boot detection, also serves as a fixed time we can produce input timing estimates with
    if VBlankCounter == lowVBlankHeralding:
        tic = time()

    # Attempt to grab seed
    if VBlankCounter == APressValue:
        if repeatCounter > 0:
            bot.pause(delay * repeatCounter)

        bot.press("A")
        toc = time()

        # Stall until seed is initialized
        ok = True

        while not bot.read_is_box_pointer_initialized():
            if time() - toc > 3:
                ok = False
                break

            bot.pause(0.001)

        # Seed initialization timed out, reset and try again
        if not ok:
            print("Failed to press A at the cutscene")
            consecutiveFailures += 1
            tic = 0
            toc = 0
            bot.restart_game()
            bot.pause(1)
            resetTime = time()
            continue

        # Collect data
        initialSeed = bot.read_initial_seed()
        seedsCounter += 1
        print(
            f"{seedsCounter:04d} - {initialSeed:04X} | {APressValue} ({(toc - tic):.4f})"
        )

        with open(outputFileName, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([f"{initialSeed:04X}", APressValue, toc - tic])

        repeatCounter += 1

        if repeatCounter == repeatTimes:
            repeatCounter = 0
            APressValue += 1

        consecutiveFailures = 0
        tic = 0
        toc = 0
        bot.restart_game()
        resetTime = time()
    elif VBlankCounter > APressValue and tic != 0:
        print("Missed frame to press A")
        consecutiveFailures += 1
        tic = 0
        toc = 0
        bot.restart_game()
        bot.pause(1)
        resetTime = time()
        continue

    bot.pause(0.001)
