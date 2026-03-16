import signal, json, csv, os
from time import time
from seed_bot import SeedBot

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

bot = SeedBot(config["IP"])
INITIAL_SEED_DELAY = config["A_PRESS_INITIAL_VALUE"]
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

delay = 16.7427 / 1000 / REPEAT_TIMES
reset_time = time()
consecutive_failures = 0

# Make file with header if file did not already exist
if not os.path.exists(OUTPUT_FILE_NAME):
    with open(OUTPUT_FILE_NAME, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Seed", "Frame", "Time"])

blink_start_good_values = [0 for _ in range(90)]
data_zero = 0
data_one = 0
data_two = 0

for i in range(90):
    if data_one:
        data_two = 30
    else:
        data_two = 60

    data_zero += 1

    if data_zero > data_two:
        data_zero = 0
        data_one ^= 1

    blink_start_good_values[i] = (data_two << 32) | (data_one << 16) | data_zero

seed_delay = INITIAL_SEED_DELAY + seeds_counter

while (
    seeds_counter < SEEDS_TO_COLLECT
    and consecutive_failures < 5
):
    # Verify the game booted and get a time stamp for an event with fixed-time relative to boot
    try:
        vblank_counter = bot.read_vblank_counter()

        while vblank_counter != LOW_VBLANK_HERALDING:
            if time() - reset_time > 10:
                print("Failed to boot")
                raise TimeoutError

            bot.pause(0.001)
            vblank_counter = bot.read_vblank_counter()

        tic = time()
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM, restarting the game and resetting the connection in 15 seconds"
        )
        tic = 0
        toc = 0
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

    # Stall until the BlinkPressStart task has been initialized
    try:
        while not bot.is_blink_start_initialized():
            bot.pause(0.001)
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM, restarting the game and resetting the connection in 15 seconds"
        )
        tic = 0
        toc = 0
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

    # Stall until the right number of main game loops have occured
    loop_counter = 0
    prior_blink_data = 0

    try:
        while loop_counter < seed_delay:
            bot.pause(0.001)
            blink_data = bot.read_blink_start_counter()
            index = loop_counter % 90
            # Data matches the next expected value in the sequence

            if blink_data == blink_start_good_values[index]:
                loop_counter += 1
                prior_blink_data = blink_data
            else:
                # Data is same as old data
                if blink_data == prior_blink_data:
                    continue

                prior_zero = prior_blink_data & 0xFFFF
                prior_one = (prior_blink_data >> 16) & 0xFFFF
                prior_two = (prior_blink_data >> 32) & 0xFFFF

                if prior_one == 1:
                    prior_two = 30
                else:
                    prior_two = 60

                # There are a number of edge cases that would only happen extremely rarely if we read in the middle of the function that we test for
                test_prior = (prior_two << 32) | (prior_one << 16) | prior_zero

                if prior_blink_data == test_prior:
                    continue

                prior_zero += 1
                test_prior = (prior_two << 32) | (prior_one << 16) | prior_zero

                if prior_blink_data == test_prior:
                    continue

                if prior_zero >= prior_two:
                    prior_zero = 0
                    test_prior = (prior_two << 32) | (prior_one << 16) | prior_zero

                    if prior_blink_data == test_prior:
                        continue

                    prior_one ^= 1
                    test_prior = (prior_two << 32) | (prior_one << 16) | prior_zero

                    if prior_blink_data == test_prior:
                        continue

                # None of the test cases made sense, so we raise an error because we don't understand where we are in the cycle
                raise ValueError(f"New data {blink_data} not consistent with old data {prior_blink_data}")
    except ValueError as e:
        print(e)
        tic = 0
        toc = 0
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue
    except Exception as e:
        print(
            "Error reading RAM, restarting the game and resetting the connection in 15 seconds"
        )
        tic = 0
        toc = 0
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

    # A press to trigger seed
    bot.press("A")
    toc = time()


    # Stall until seed is initialized
    ok = True

    try:
        while not bot.read_is_box_pointer_initialized():
            if time() - toc > 3:
                ok = False
                break

            bot.pause(0.001)
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM, restarting the game and resetting the connection in 15 seconds"
        )
        tic = 0
        toc = 0
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

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
    try:
        initial_seed = bot.read_initial_seed()
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM, restarting the game and resetting the connection in 15 seconds"
        )
        tic = 0
        toc = 0
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

    seeds_counter += 1
    print(
        f"{seeds_counter:04d} - {initial_seed:04X} | {seed_delay} ({(toc - tic):.4f})"
    )

    with open(OUTPUT_FILE_NAME, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([f"{initial_seed:04X}", seed_delay, toc - tic])

    repeat_counter += 1

    if repeat_counter == REPEAT_TIMES:
        repeat_counter = 0
        seed_delay += 1

    consecutive_failures = 0
    tic = 0
    toc = 0
    bot.restart_game()
    reset_time = time()
