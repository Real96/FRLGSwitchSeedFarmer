# Go to root/test of PyNXBot
import signal, json, csv
from time import time
from PySysBot import FRLGBot

config = json.load(open("config.json"))
b = FRLGBot(config["IP"])
APressInitialValue = config["APressInitialValue"]
APressUpperLimit = config["APressUpperLimit"]
seedsToCollect = config["seedsToCollect"]
repeatTimes = config["repeatTimes"]
outputFileName = config["outputFileName"]


def signal_handler(_signal, _advances):  # CTRL+C handler
    print("Stop request")
    b.close()


signal.signal(signal.SIGINT, signal_handler)


def restart():
    b.release("A")
    b.quitGame()
    b.enterGame(False)


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
try:
    file = open(outputFileName, "r")
except FileNotFoundError:
    file = open(outputFileName, "w", newline="")
    writer = csv.writer(file)
    writer.writerow(["Seed", "Frame", "Time"])
finally:
    if file is not None:
        file.close()

while (
    seedsCounter < seedsToCollect
    and APressValue <= APressUpperLimit
    and consecutiveFailures < 5
):
    try:
        VBlankCounter = b.getVBlankCounter()
    except Exception as e:
        print("Error reading, resetting")
        restart()
        b.pause(1)
        resetTime = time()
        consecutiveFailures += 1
        continue

    # Check if we have not reached our "boot succeeded" detection within 5 seconds, reset if need be
    if tic == 0 and time() - resetTime > 10:
        # We failed to properly boot, try again
        print("Failed to boot")
        consecutiveFailures += 1
        restart()
        b.pause(1)
        resetTime = time()
        continue

    # Early boot detection, also serves as a fixed time we can produce input timing estimates with
    if VBlankCounter == lowVBlankHeralding:
        tic = time()

    # Attempt to grab seed
    if VBlankCounter == APressValue:
        if repeatCounter > 0:
            b.pause(delay * repeatCounter)

        b.press("A")
        toc = time()

        # Stall until seed is initialized
        ok = True

        while not b.isBoxPointerInitialized():
            if time() - toc > 3:
                ok = False
                break

            b.pause(0.001)

        # Seed initialization timed out, reset and try again
        if not ok:
            print("Failed to press A at the cutscene")
            consecutiveFailures += 1
            tic = 0
            toc = 0
            restart()
            b.pause(1)
            resetTime = time()
            continue

        # Collect data
        initialSeed = b.getInitialSeed()
        seedsCounter += 1
        print(
            f"{seedsCounter:04d} - {initialSeed:04X} | {APressValue} ({(toc - tic):.4f})"
        )

        with open(outputFileName, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([f"{initialSeed:04X}", APressValue, toc - tic])

        repeatCounter += 1

        if repeatCounter == repeatTimes:
            repeatCounter = 0
            APressValue += 1

        consecutiveFailures = 0
        tic = 0
        toc = 0
        restart()
        resetTime = time()
    elif VBlankCounter > APressValue and tic != 0:
        print("Missed frame to press A")
        consecutiveFailures += 1
        tic = 0
        toc = 0
        restart()
        b.pause(1)
        resetTime = time()
        continue

    b.pause(0.001)
