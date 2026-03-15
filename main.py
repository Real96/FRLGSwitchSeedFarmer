# Go to root/test of PyNXBot
import signal, json, csv, os
from time import time
from seed_bot import SeedBot

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

bot = SeedBot(config["IP"])
A_PRESS_INITIAL_VALUE = config["A_PRESS_INITIAL_VALUE"]
A_PRESS_UPPER_LIMIT = config["A_PRESS_UPPER_LIMIT"]
SEEDS_TO_COLLECT = config["SEEDS_TO_COLLECT"]
REPEAT_TIMES = config["REPEAT_TIMES"]
OUTPUT_FILE_NAME = config["OUTPUT_FILE_NAME"]
DEBUG = config["DEBUG"]


def signal_handler(_signal, _advances):  # CTRL+C handler
    print("Stop request")
    bot.close()


signal.signal(signal.SIGINT, signal_handler)

LOW_VBLANK_HERALDING = 256
seeds_counter = 0
vblank_counter = 0
repeat_counter = 0
tic = 0
toc = 0

a_press_value = A_PRESS_INITIAL_VALUE
delay = 16.7427 / 1000 / REPEAT_TIMES
reset_time = time()
consecutive_failures = 0

# Make file with header if file did not already exist
if not os.path.exists(OUTPUT_FILE_NAME):
    with open(OUTPUT_FILE_NAME, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Seed", "Frame", "Time"])

while (
    seeds_counter < SEEDS_TO_COLLECT
    and a_press_value <= A_PRESS_UPPER_LIMIT
    and consecutive_failures < 5
):
    try:
        vblank_counter = bot.read_vblank_counter()

        if DEBUG:
            print(f"VBlank: {vblank_counter}")
    # TODO: actual exception types
    except Exception:
        print("Error reading RAM, restarting the game and resetting the connection in 15 seconds")
        tic = 0
        toc = 0
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

    # Check if we have not reached our "boot succeeded" detection within 10 seconds, reset if need be
    if tic == 0 and time() - reset_time > 10:
        # We failed to properly boot, try again
        print("Failed to boot")
        tic = 0
        toc = 0
        consecutive_failures += 1
        bot.restart_game()
        bot.pause(1)
        reset_time = time()
        continue

    # Early boot detection, also serves as a fixed time we can produce input timing estimates with
    if vblank_counter == LOW_VBLANK_HERALDING:
        tic = time()

    # Attempt to grab seed
    if vblank_counter == a_press_value:
        if repeat_counter > 0:
            bot.pause(delay * repeat_counter)

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
            consecutive_failures += 1
            tic = 0
            toc = 0
            bot.restart_game()
            bot.pause(1)
            reset_time = time()
            continue

        # Collect data
        initialSeed = bot.read_initial_seed()
        seeds_counter += 1
        print(
            f"{seeds_counter:04d} - {initialSeed:04X} | {a_press_value} ({(toc - tic):.4f})"
        )

        with open(OUTPUT_FILE_NAME, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([f"{initialSeed:04X}", a_press_value, toc - tic])

        repeat_counter += 1

        if repeat_counter == REPEAT_TIMES:
            repeat_counter = 0
            a_press_value += 1

        consecutive_failures = 0
        tic = 0
        toc = 0
        bot.restart_game()
        reset_time = time()
    elif vblank_counter > a_press_value and tic != 0:
        print("Missed frame to press A")
        consecutive_failures += 1
        tic = 0
        toc = 0
        bot.restart_game()
        bot.pause(1)
        reset_time = time()
        continue

    bot.pause(0.001)
