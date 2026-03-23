import signal, json, csv, os
from time import perf_counter
from collections import Counter
from seed_bot import SeedBotIP, SeedBotUSB

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

INITIAL_SEED_DELAY = config["FIRST_SEED_TO_COLLECT"]
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

bot = (
    SeedBotUSB(config["USB_INDEX"], config["SKIP_PROFILE"])
    if USB
    else SeedBotIP(config["IP"], config["SKIP_PROFILE"])
)


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

if DEBUG and USB:
    bot.send_command("configure enableLogs 1")

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
current_times = []
prior_time = None
reconnect = False
bot.press("A")
bot.pause(5)

while seeds_counter < SEEDS_TO_COLLECT and consecutive_failures < 5:
    # Verify the game booted and get a time stamp for an event with fixed-time relative to boot
    loop_counter = 0
    prior_blink_data = 0
    tic = 0
    toc = 0
    # Boot time measurement statistics never had a value outside range of 2.5 to 3.1 seconds
    # shift those endpoints by 100ms and round the ms per frame down/up accordingly for safety
    # vblankCounter is reset to zero approximately 16 frames post boot by the bootup process.
    first_read_delay = 0 + (LOW_VBLANK_HERALDING + 16) * 0.016
    vblank_timeout = 0.8 + (LOW_VBLANK_HERALDING + 16) * 0.017

    if reconnect:
        first_read_delay -= 1.5
        vblank_timeout -= 1.5

    bot.restart_game(should_reconnect=reconnect, button=SEED_BUTTON)
    reset_time = perf_counter()

    if DEBUG:
        print(f"Finished resetting, pausing for {first_read_delay} seconds")

    bot.pause(first_read_delay)

    if DEBUG:
        print("Reading VBlank counter until heralded value appears")

    try:
        vblank_counter = bot.read_vblank_counter()

        if DEBUG:
            print(f"VBlank: {vblank_counter}")

        while vblank_counter != LOW_VBLANK_HERALDING:
            if perf_counter() - reset_time > vblank_timeout:
                print(f"Failed to latch herald vblank value of {LOW_VBLANK_HERALDING}.")
                raise TimeoutError

            bot.pause(0.002)
            vblank_counter = bot.read_vblank_counter()

            if DEBUG:
                print(f"VBlank: {vblank_counter}")

        tic = perf_counter()
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM for vblank, restarting the game and resetting the connection in 15 seconds"
        )
        bot.pause(15)
        reconnect = True
        consecutive_failures += 1
        continue

    if DEBUG:
        print("Heralded value was found, pausing for 24 seconds")

    # Stall until the BlinkPressStart task has been initialized
    bot.pause(24)

    if seed_delay == 0:
        if DEBUG:
            print("Attempting to detect title screen scene run")

        try:
            first_task_data = bot.read_first_task_data()

            while first_task_data != 3:
                if perf_counter() - tic > 25:
                    raise TimeoutError(
                        "Timed out waiting to detect last scene of Fadein"
                    )

                bot.pause(0.001)

                if DEBUG:
                    print(hex(first_task_data))

                first_task_data = bot.read_first_task_data()
        except TimeoutError as e:
            print(e)
            bot.pause(15)
            reconnect = True
            consecutive_failures += 1
            continue
        except Exception:
            print(
                "Error reading RAM for title screen scene, restarting the game and resetting the connection in 15 seconds"
            )
            bot.pause(15)
            reconnect = True
            consecutive_failures += 1
            continue
    else:
        if DEBUG:
            print("Attempting to detect BLINK_START task")

        try:
            task_two_pointer = bot.read_task_two_pointer()

            if DEBUG:
                print(f"Task two function is {hex(task_two_pointer)}")

            while task_two_pointer != bot.blink_start_value:
                if perf_counter() - tic > 25:
                    raise TimeoutError("Timed out waiting to detect BLINK_START task")

                bot.pause(0.001)
                task_two_pointer = bot.read_task_two_pointer()

                if DEBUG:
                    print(f"Task two function is {hex(task_two_pointer)}")

        except TimeoutError as e:
            print(e)
            bot.pause(15)
            reconnect = True
            consecutive_failures += 1
            continue
        except Exception:
            print(
                "Error reading RAM for blink start task, restarting the game and resetting the connection in 15 seconds"
            )
            bot.pause(15)
            reconnect = True
            consecutive_failures += 1
            continue

        if DEBUG:
            print(
                "Following chain of BLINK_START counters to delay press appropriately"
            )

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
            bot.pause(15)
            reconnect = True
            consecutive_failures += 1
            continue
        except Exception as e:
            print(
                "Error reading RAM for blink start state, restarting the game and resetting the connection in 15 seconds"
            )
            bot.pause(15)
            reconnect = True
            consecutive_failures += 1
            continue

    # A press to trigger seed
    bot.press(SEED_BUTTON)
    toc = perf_counter()

    if DEBUG:
        print("PRESSED A to get seed, pausing for 2.05 seconds to wait for latch")

    this_time = toc - tic
    bot.pause(2.05)

    if DEBUG:
        print(
            "Attempting to detect box pointer initialization to know seed read is safe"
        )

    # Stall until seed is initialized
    ok = True

    try:
        while not bot.read_is_box_pointer_initialized():
            if perf_counter() - toc > 3:
                ok = False
                break

            bot.pause(0.2)
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM for box pointer, restarting the game and resetting the connection in 15 seconds"
        )
        bot.pause(15)
        reconnect = True
        consecutive_failures += 1
        continue

    # Seed initialization timed out, reset and try again
    if not ok:
        print("Failed to press A at the cutscene")
        reconnect = True
        consecutive_failures += 1
        continue

    if DEBUG:
        print("Reading Seed")

    # Collect data
    try:
        initial_seed = bot.read_initial_seed()
    # TODO: actual exception types
    except Exception:
        print(
            "Error reading RAM for seed, restarting the game and resetting the connection in 15 seconds"
        )
        bot.pause(15)
        reconnect = True
        consecutive_failures += 1
        continue

    seeds_counter += 1
    print(
        f"{seeds_counter:04d} - {initial_seed:04X} | {seed_delay} ({(this_time):.4f})"
    )

    if REPEAT_MODE == "FIXED":
        # "FIXED" mode records all entries
        repeat_counter += 1

        with open(OUTPUT_FILE_NAME, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([f"{initial_seed:04X}", seed_delay, this_time])

        if repeat_counter == REPEAT_TIMES:
            repeat_counter = 0
            seed_delay += 1
    else:
        # "AUTO" mode checks for apparent timing discrepencies, will only commit entries once a unique mode emerges
        if prior_time and (this_time - prior_time > 0.05 or this_time < prior_time):
            print("Apparent discrepency. Discarding last measurement")
        else:
            current_seeds.append(initial_seed)
            current_times.append(this_time)
            counts = Counter(current_seeds)
            two_most_frequent = counts.most_common(2)

            if two_most_frequent[0][
                1
            ] > 1 and (  # Most common seed has appeared multiple times
                len(two_most_frequent) == 1  # Most common seed is only seed
                or two_most_frequent[0][1] > two_most_frequent[1][1]
            ):  # Multiple seeds, but unique mode
                most_frequent_seed = two_most_frequent[0][0]
                t = 0

                with open(OUTPUT_FILE_NAME, "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)

                    for seed_entry, time_entry in zip(current_seeds, current_times):
                        if seed_entry == most_frequent_seed:
                            writer.writerow(
                                [f"{seed_entry:04X}", seed_delay, time_entry]
                            )
                            t += time_entry

                prior_time = t / two_most_frequent[0][1]
                seed_delay += 1
                current_seeds = []
                current_times = []

    if DEBUG:
        print("No problems. Resetting for next cycle")

    consecutive_failures = 0
    reconnect = False
