import sys, socket, binascii
from time import sleep

GAMES = {
    0x1006FA0233F8000: {
        "Game": "FireRed (JPN)",
        "VBlankCounter": 0xBD68B304,
        "CurrentSeedAddress": 0xBD68D230,
        "BlinkStartValue": 0x807CB99 # to change
    },
    0x100F1E0233FA000: {
        "Game": "LeafGreen (JPN)",
        "VBlankCounter": 0xBD68B304,
        "CurrentSeedAddress": 0xBD68D230,
        "BlinkStartValue": 0x807CB99 # to change
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
        "BlinkStartValue": 0x807CB99 # to change
    },
    0x10087C02342E000: {
        "Game": "LeafGreen (FRE)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99 # to change
    },
    0x10092302342A000: {
        "Game": "FireRed (ITA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99
    },
    0x1005C7023432000: {
        "Game": "LeafGreen (ITA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99
    },
    0x1007F8023416000: {
        "Game": "FireRed (GER)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99 # to change
    },
    0x100FD6023430000: {
        "Game": "LeafGreen (GER)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99 # to change
    },
    0x100EB702342C000: {
        "Game": "FireRed (SPA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99 # to change
    },
    0x1002B5023434000: {
        "Game": "LeafGreen (SPA)",
        "VBlankCounter": 0xBD68B2F4,
        "CurrentSeedAddress": 0xBD68D220,
        "BlinkStartValue": 0x807CB99 # to change
    },
}


class SeedBot:
    def __init__(self, ip):
        self.connect(ip)
        self.detect_game()

    def connect(self, ip):
        self.ip = ip
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((self.ip, 6000))
        print("Bot Connected")
        self.send_command("configure echoCommands 0")

    def detect_game(self):
        title_id = self.get_title_id()
        if title_id == 0:
            print("Game not running, starting it and resetting the connection")
            self.restart_game(True)
        elif title_id not in GAMES:
            print(f"Unsupported title: {title_id:016X}")
            self.close()
        else:
            game_info = GAMES[title_id]
            self.game_name = game_info["Game"]
            self.current_seed_address = game_info["CurrentSeedAddress"]
            self.vblank_counter_address = game_info["VBlankCounter"]
            self.blink_start_value = game_info["BlinkStartValue"]
            print(f"Game: {self.game_name}\n")

    def send_command(self, content):
        content += "\r\n"  # important for the parser on the switch side
        self.s.sendall(content.encode())

    def detach(self):
        self.send_command("detachController")

    def close(self, exitapp=True):
        print("Exiting...")
        self.pause(0.5)
        self.detach()
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        print("Bot Disconnected")
        if exitapp:
            sys.exit(0)

    # A/B/X/Y/LSTICK/RSTICK/L/R/ZL/ZR/PLUS/MINUS/DLEFT/DUP/DDOWN/DRIGHT/HOME/CAPTURE
    def click(self, button):
        self.send_command("click " + button)

    def press(self, button):
        self.send_command("press " + button)

    def release(self, button):
        self.send_command("release " + button)

    # peek <address in hex, prefaced by 0x> <amount of bytes, dec or hex with 0x>
    def read(self, address, size):
        self.send_command(f"peek 0x{address:X} 0x{size:X}")
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

    def pause(self, duration):
        sleep(duration)

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

    def enter_game(self):
        self.click("A")
        self.pause(0.2)
        self.click("A")
        self.pause(1.3)
        self.click("A")
        self.pause(0.2)
        self.click("A")

    def restart_game(self, should_reconnect=False):
        self.release("A")
        self.quit_game()
        self.enter_game()

        if should_reconnect:
            self.close(False)
            self.pause(1.5)
            self.connect(self.ip)
            self.detect_game()

    def read_initial_seed(self):
        return int.from_bytes(self.read(0x1208000, 2), "little")

    def read_current_seed(self):
        return int.from_bytes(self.read(self.current_seed_address, 4), "little")

    def read_vblank_counter(self):
        return int.from_bytes(self.read(self.vblank_counter_address, 4), "little")

    def read_is_box_pointer_initialized(self):
        return (
            int.from_bytes(self.read(self.current_seed_address + 0x10, 4), "little")
            != 0
        )

    def read_is_blink_start_initialized(self):
        return (
            int.from_bytes(self.read(self.current_seed_address + 0xE0, 4), "little")
            == self.blink_start_value
        )

    def read_blink_start_counter(self):
        return int.from_bytes(self.read(self.current_seed_address + 0xE8, 16), "little")
