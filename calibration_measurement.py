import json, signal
from seed_bot import SeedBot, SeedBotUSB
from time import perf_counter

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

USB = config["USB"]
DEBUG = config["DEBUG"]

bot = (
    SeedBotUSB(config["USB_INDEX"], config["SKIP_PROFILE"])
    if USB
    else SeedBot(config["IP"], config["SKIP_PROFILE"])
)


def signal_handler(_signal, _advances):  # CTRL+C handler
    print("Stop request")
    bot.close()


signal.signal(signal.SIGINT, signal_handler)

LOW_VBLANK_HERALDING = 256
reset_times = []
reconnect = False
bot.press("A")
bot.pause(5)
loop_counter = 0

while loop_counter < 30:
    # Verify the game booted and get a time stamp for an event with fixed-time relative to boot
    tic = 0
    reset_time = 0
    # Boot time measurement statistics never had a value outside range of 2.5 to 3.1 seconds
    # shift those endpoints by 100ms and round the ms per frame down/up accordingly for safety
    # vblankCounter is reset to zero approximately 16 frames post boot by the bootup process.
    first_read_delay = 0 + (LOW_VBLANK_HERALDING + 16) * 0.016
    vblank_timeout = 0.8 + (LOW_VBLANK_HERALDING + 16) * 0.017

    if reconnect:
        first_read_delay -= 1.5
        vblank_timeout -= 1.5

    bot.restart_game(should_reconnect=reconnect)
    reset_time = perf_counter()

    if DEBUG:
        print(f"Finished resetting, pausing for {first_read_delay} seconds")

    bot.pause(first_read_delay)

    if DEBUG:
        print("Reading Vblank counter until heralded value appears")

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
        continue

    this_time = tic - reset_time
    reset_times.append(this_time)
    print(
        f"Measured a time of {this_time}. Running average is {sum(reset_times) / len(reset_times)}"
    )
    loop_counter += 1

print(reset_times)
