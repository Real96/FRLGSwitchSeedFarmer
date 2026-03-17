import signal, json, csv, os
from time import time
from seed_bot import SeedBot, SeedBotUSB

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
INITIAL_SEED_DELAY = config["A_PRESS_INITIAL_VALUE"]
SEEDS_TO_COLLECT = config["SEEDS_TO_COLLECT"]
REPEAT_MODE = config["REPEAT_MODE"]
SEED_BUTTON = config["SEED_BUTTON"]
if SEED_BUTTON not in ["A", "X", "L", "START", "PLUS"]:
    raise ValueError(
    f"{SEED_BUTTON} is not a valid seed button. Must be one of 'A', 'START', 'X', 'PLUS', or 'L'."
    )
if SEED_BUTTON == "START":
    SEED_BUTTON = "X"

if REPEAT_MODE == "FIXED":
    REPEAT_TIMES = config["REPEAT_TIMES"]
elif REPEAT_MODE == "AUTO":
    REPEAT_TIMES = None
else:
    raise ValueError(
    f"{REPEAT_MODE} is an invalid value for REPEAT_MODE. Acceptable values are 'AUTO' or 'FIXED'."
    )

OUTPUT_FILE_NAME = config["OUTPUT_FILE_NAME"]
USB = config["USB"]
DEBUG = config["DEBUG"]
EMUNAND = config["EMUNAND"]

bot = SeedBotUSB() if USB else SeedBot(config["IP"])

def signal_handler(_signal, _advances):  # CTRL+C handler
    print("Stop request")
    bot.close()

signal.signal(signal.SIGINT, signal_handler)

LOW_VBLANK_HERALDING = 256
seeds_counter = 0
vblank_counter = 0
repeat_counter = 0
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

    if data_zero >= data_two:
        data_zero = 0
        data_one ^= 1

    blink_start_good_values[i] = (data_two << 32) | (data_one << 16) | data_zero

blink_start_good_values = tuple(blink_start_good_values)
seed_delay = INITIAL_SEED_DELAY + seeds_counter
current_seeds = []
reset_time = time()

while seeds_counter < SEEDS_TO_COLLECT and consecutive_failures < 5:
    # Verify the game booted and get a time stamp for an event with fixed-time relative to boot
    loop_counter = 0
    prior_blink_data = 0
    tic = 0
    toc = 0
    bot.pause(1)

    try:
        vblank_counter = bot.read_vblank_counter()

        while vblank_counter != LOW_VBLANK_HERALDING:
            if time() - reset_time > 10:
                print("Failed to boot")
                raise TimeoutError

            bot.pause(0.001)
            vblank_counter = bot.read_vblank_counter()

            if DEBUG:
                print(f"VBlank: {vblank_counter}")

        tic = time()
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM for vblank, restarting the game and resetting the connection in 15 seconds"
        )
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

    # Stall until the BlinkPressStart task has been initialized
    bot.pause(24)

    if seed_delay == 0:
        try:
            first_task_data = bot.read_first_task_data()

            while first_task_data != 3:
                bot.pause(0.001)
                if DEBUG:
                    print(hex(first_task_data))
                first_task_data = bot.read_first_task_data()

        except Exception:
            print(
                "Error reading RAM for title screen scene, restarting the game and resetting the connection in 15 seconds"
            )
            bot.pause(15)
            bot.restart_game(True)
            reset_time = time()
            consecutive_failures += 1
            continue

    else:
        try:
            task_two_pointer = bot.read_task_two_pointer()
            while task_two_pointer != bot.blink_start_value:
                if DEBUG:
                    print(f"Task two function is {hex(task_two_pointer)}")
                bot.pause(0.001)
            task_two_pointer = bot.read_task_two_pointer()
                
        # TODO: actual exception types
        except Exception:
            print(
                "Error reading RAM for blink start task, restarting the game and resetting the connection in 15 seconds"
            )
            bot.pause(15)
            bot.restart_game(True)
            reset_time = time()
            consecutive_failures += 1
            continue

        # Stall until the right number of main game loops have occured
        try:
            while loop_counter < seed_delay - 1:
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

                    if prior_one == 1:
                        base = 0x1E00010000
                    else:
                        base = 0x3C00000000

                    # There are a number of edge cases that would only happen extremely rarely if we read in the middle of the function that we test for
                    test_prior = base | prior_zero

                    if blink_data == test_prior:
                        prior_blink_data = blink_start_good_values[index]
                        loop_counter += 1
                        continue

                    prior_zero += 1
                    test_prior = base | prior_zero

                    if blink_data == test_prior:
                        prior_blink_data = blink_start_good_values[index]
                        loop_counter += 1
                        continue

                    prior_two = base >> 32

                    if prior_zero >= prior_two:
                        test_prior = base

                        if blink_data == test_prior:
                            prior_blink_data = blink_start_good_values[index]
                            loop_counter += 1
                            continue

                    # None of the test cases made sense, so we raise an error because we don't understand where we are in the cycle
                    raise ValueError(
                        f"New data {blink_data} not consistent with old data {prior_blink_data}"
                    )
        except ValueError as e:
            print(e)
            bot.pause(15)
            bot.restart_game(True)
            reset_time = time()
            consecutive_failures += 1
            continue
        except Exception as e:
            print(
                "Error reading RAM for blink start state, restarting the game and resetting the connection in 15 seconds"
            )
            bot.pause(15)
            bot.restart_game(True)
            reset_time = time()
            consecutive_failures += 1
            continue

    # A press to trigger seed
    bot.press(SEED_BUTTON)
    toc = time()

    # Stall until seed is initialized
    ok = True
    try:
        while not bot.read_is_box_pointer_initialized():
            if time() - toc > 5:
                ok = False
                break
                bot.pause(0.2)

    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM for box pointer, restarting the game and resetting the connection in 15 seconds"
        )
        bot.pause(15)
        bot.restart_game(True)
        reset_time = time()
        consecutive_failures += 1
        continue

    # Seed initialization timed out, reset and try again
    if not ok:
        print("Failed to press A at the cutscene")
        consecutive_failures += 1
        bot.restart_game(True)
        reset_time = time()
        continue

    # Collect data
    try:
        initial_seed = bot.read_initial_seed()
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM for seed, restarting the game and resetting the connection in 15 seconds"
        )
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

    if REPEAT_MODE == "FIXED":
        repeat_counter += 1

        if repeat_counter == REPEAT_TIMES:
            repeat_counter = 0
            seed_delay += 1
    else:
        if len(current_seeds) == 0 or len(current_seeds) == 1 and current_seeds[0] != initial_seed:
            current_seeds.append(initial_seed)
        else:
            seed_delay += 1
            current_seeds = []

    consecutive_failures = 0
    bot.restart_game()

    if EMUNAND:
        bot.pause(1.6)

    reset_time = time()
