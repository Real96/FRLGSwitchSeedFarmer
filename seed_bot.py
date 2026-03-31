from abc import ABC, abstractmethod
import sys, socket, binascii, json
from usb import core, util
from time import sleep, perf_counter

GAMES = {
    0x1006FA0233F8000: {
        "Game": "FireRed (JPN)",
        "VBlankCounter": 0xBD68B304,
        "CurrentSeedAddress": 0xBD68D230,
        "BlinkStartValue": 0x807C3A1,
    },
    0x100F1E0233FA000: {
        "Game": "LeafGreen (JPN)",
        "VBlankCounter": 0xBD68B304,
        "CurrentSeedAddress": 0xBD68D230,
        "BlinkStartValue": 0x807C3A1,
    },
    0x100554023408000: {
        "Game": "FireRed (ENG)",
        "VBlankCounter": 0xBD68B3A4,
        "CurrentSeedAddress": 0xBD68D2D0,
        "BlinkStartValue": 0x807CB65,
    },
    0x10034D02340E000: {
        "Game": "LeafGreen (ENG)",
        "VBlankCounter": 0xBD68B3A4,
        "CurrentSeedAddress": 0xBD68D2D0,
        "BlinkStartValue": 0x807CB65,
    },
    0x1004B3023412000: {
        "Game": "FireRed (FRE)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CC6D,
    },
    0x10087C02342E000: {
        "Game": "LeafGreen (FRE)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CC6D,
    },
    0x10092302342A000: {
        "Game": "FireRed (ITA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99,
    },
    0x1005C7023432000: {
        "Game": "LeafGreen (ITA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99,
    },
    0x1007F8023416000: {
        "Game": "FireRed (GER)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CBAD,
    },
    0x100FD6023430000: {
        "Game": "LeafGreen (GER)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CBAD,
    },
    0x100EB702342C000: {
        "Game": "FireRed (SPA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CC81,
    },
    0x1002B5023434000: {
        "Game": "LeafGreen (SPA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CC81,
    },
}


class SeedBot(ABC):
    def __init__(self, skip_profile):
        self.skip_profile = skip_profile
        self.connect()
        self.detect_game()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def _send(self, data):
        pass

    @abstractmethod
    def _read(self, size) -> bytes:
        pass

    @abstractmethod
    def get_title_id(self) -> int:
        pass

    @abstractmethod
    def shutdown(self):
        pass

    def send_command(self, content):
        content += "\r\n"  # important for the parser on the switch side
        self._send(content.encode())

    # peek <address in hex, prefaced by 0x> <amount of bytes, dec or hex with 0x>
    def read(self, address, size):
        self.send_command(f"peek 0x{address:X} 0x{size:X}")

        return self._read(size)

    # A/B/X/Y/LSTICK/RSTICK/L/R/ZL/ZR/PLUS/MINUS/DLEFT/DUP/DDOWN/DRIGHT/HOME/CAPTURE
    def click(self, button):
        self.send_command("click " + button)

    def press(self, button):
        self.send_command("press " + button)

    def release(self, button):
        self.send_command("release " + button)

    def pause(self, duration):
        sleep(duration)

    def detach(self):
        self.send_command("detachController")

    def close(self, exitapp=True):
        print("Exiting...")
        self.pause(0.5)
        self.detach()
        self.shutdown()

        print("Bot Disconnected")

        if exitapp:
            sys.exit(0)

    def enter_game(self):
        self.click("A")
        self.pause(0.2)
        self.click("A")

        if not self.skip_profile:
            self.pause(1.3)
            self.click("A")
            self.pause(0.2)
            self.click("A")

    def quit_game(self):
        self.click("HOME")
        self.pause(0.8)
        self.click("X")
        self.pause(0.2)
        self.click("X")
        self.pause(0.4)
        self.click("A")
        self.pause(0.2)
        self.click("A")
        self.pause(1.3)

    def restart_game(self, should_reconnect=False, button="A", quit_game=True):
        self.release(button)
        self.pause(0.05)

        if quit_game:
            self.quit_game()

        self.enter_game()

        if should_reconnect:
            self.close(False)
            self.pause(1.5)
            self.connect()
            self.detect_game()

    def detect_game(self):
        title_id = self.get_title_id()

        if title_id == 0:
            print("Game not running, starting it and resetting the connection")
            self.restart_game(should_reconnect=True, quit_game=False)
        elif title_id not in GAMES:
            print(f"Unsupported title: {title_id:016X}")
            self.close()
        else:
            game_info = GAMES[title_id]
            self.game_name = game_info["Game"]
            self.initial_seed_address = 0x1208000
            self.current_seed_address = game_info["CurrentSeedAddress"]
            self.vblank_counter_address = game_info["VBlankCounter"]
            self.blink_start_value = game_info["BlinkStartValue"]
            print(f"Game: {self.game_name}\n")
            print(f"Sound: {self.read_options_sound()}")
            print(f"Button Mode: {self.read_options_button_mode()}")

            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"""Seed button: {config["SEED_BUTTON"]}\n""")

    def read_initial_seed(self):
        return int.from_bytes(self.read(self.initial_seed_address, 2), "little")

    def read_current_seed(self):
        return int.from_bytes(self.read(self.current_seed_address, 4), "little")

    def read_vblank_counter(self):
        return int.from_bytes(self.read(self.vblank_counter_address, 4), "little")

    def read_is_box_pointer_initialized(self):
        return (
            int.from_bytes(self.read(self.current_seed_address + 0x10, 4), "little")
            != 0
        )

    def read_options_bitfield(self):
        return int.from_bytes(
            self.read(
                int.from_bytes(self.read(self.current_seed_address + 0xC, 4), "little")
                - 0x2020000
                + self.initial_seed_address
                + 0x13,
                3,
            ),
            "little",
        )

    def read_options_sound(self):
        sound_mode = ["Mono", "Stereo"]

        return sound_mode[(self.read_options_bitfield()) >> 10 & 1]  # bit 9

    def read_options_button_mode(self):
        button_mode = ["Help", "LR", "L=A"]

        return button_mode[self.read_options_bitfield() & 3]  # bits 0-1

    def read_is_blink_start_initialized(self):
        return (
            int.from_bytes(self.read(self.current_seed_address + 0xE0, 4), "little")
            == self.blink_start_value
        )

    def read_task_two_pointer(self):
        return int.from_bytes(self.read(self.current_seed_address + 0xE0, 4), "little")

    def read_blink_start_counter(self):
        return int.from_bytes(self.read(self.current_seed_address + 0xE8, 16), "little")

    def is_title_screen_scene_run(self):
        return (
            int.from_bytes(self.read(self.current_seed_address + 0x98, 4), "little")
            == 3
        )

    def read_first_task_data(self):
        return int.from_bytes(self.read(self.current_seed_address + 0x98, 4), "little")


class SeedBotIP(SeedBot):
    def __init__(self, ip, skip_profile):
        self.ip = ip
        super().__init__(skip_profile)

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((self.ip, 6000))
        print("Bot Connected")
        self.send_command("configure echoCommands 0")
        self.send_command("configure mainLoopSleepTime 0")

    def _send(self, data):
        self.s.sendall(data)

    def _read(self, size):
        # TODO: sensible reading and not an arbitrary wait
        sleep(size / 0x8000)
        buf = self.s.recv(2 * size + 1)
        buf = binascii.unhexlify(buf[:-1])

        return buf

    def get_title_id(self):
        self.send_command("getTitleID")
        sleep(0.005)
        buf = self.s.recv(18)

        return int(buf[0:-1], 16)

    def shutdown(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()


class SeedBotUSB(SeedBot):
    def __init__(self, usb_index, skip_profile):
        self.usb_index = usb_index
        super().__init__(skip_profile)

    def connect(self):
        devices = list(core.find(find_all=True, idVendor=0x057E, idProduct=0x3000))

        if not devices:
            raise Exception("No Switch USB devices found")

        if self.usb_index >= len(devices):
            raise Exception(
                f"The USB index {self.usb_index} is higher than the numer of Switch USB devices found."
            )

        self.device = devices[self.usb_index]
        self.device.set_configuration()
        cfg = self.device.get_active_configuration()
        intf = cfg[(0, 0)]

        self.ep_out = util.find_descriptor(
            intf,
            custom_match=lambda e: util.endpoint_direction(e.bEndpointAddress)
            == util.ENDPOINT_OUT,
        )

        self.ep_in = util.find_descriptor(
            intf,
            custom_match=lambda e: util.endpoint_direction(e.bEndpointAddress)
            == util.ENDPOINT_IN,
        )

        if self.ep_out is None or self.ep_in is None:
            raise Exception("USB endpoints not found")

        print("Bot Connected")

    def _send(self, data: bytes):
        packet_size = len(data) + 2
        self.ep_out.write(packet_size.to_bytes(4, "little"))
        self.ep_out.write(data)

    # size here is only to match the ABC
    def _read(self, size):
        size_bytes = self.ep_in.read(4, timeout=100)
        size = int.from_bytes(size_bytes, "little")
        buf = bytearray()

        while len(buf) < size:
            chunk = self.ep_in.read(size - len(buf), timeout=500)
            buf.extend(chunk)

        return bytes(buf)

    def get_title_id(self):
        self.send_command("getTitleID")
        sleep(0.005)

        return int.from_bytes(self._read(size=8), "little")

    def shutdown(self):
        util.dispose_resources(self.device)
