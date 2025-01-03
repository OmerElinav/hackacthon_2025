import math
import random
from dataclasses import dataclass, field

import requests
from pyboy import PyBoy
import requests.adapters

LEVELS_ADDR = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]
COORDS_ADDR = [0xD362, 0xD361, 0xD35E]
HP_ADDR = [
    (0xD16C, 0xD18D),
    (0xD198, 0xD1B9),
    (0xD1C4, 0xD1E5),
    (0xD1F0, 0xD211),
    (0xD21C, 0xD23D),
    (0xD248, 0xD269),
]
BADGES_ADDR = 0xD356
BUTTONS = ["a", "b", "left", "right", "up", "down", "start", "select",]


@dataclass
class GameState:
    levels: list[int] = None
    visited_regions: set = field(default_factory=set)
    visited_regions_count: int = 0
    badges: str = None

    def update(self, read_m):
        self.levels = [read_m(a) for a in LEVELS_ADDR]
        self.badges = read_m(BADGES_ADDR)
        coords = [read_m(a) for a in COORDS_ADDR]
        map_ = coords[2]
        self.visited_regions.add(map_)
        self.visited_regions_count = len(self.visited_regions)

    def get_score(self):
        return sum(self.levels) + self.visited_regions_count * 10 + self.badges * 100


class Connection:
    def __init__(self, url):
        self.session = requests.Session()
        self.url = url

    def get_data(self):
        while True:
            try:
                data = int(self.session.get(self.url, timeout=5).content)
                return data
            except Exception as e:
                print(e)


class GameEmulation:
    def __init__(self, input_url):
        self.emulation = PyBoy("pokemon_red.gb", window="null")
        self.emulation.set_emulation_speed(0)
        self.emulation.game_wrapper.start_game()
        self.emulation.tick(5)
        self.connection = Connection(input_url)

    def run(self):
        button = None
        state = GameState()
        i = 0
        while True:
            i += 10
            for x in range(9):
                button = BUTTONS[self.connection.get_data()]
                self.emulation.button(button)
                self.emulation.tick(1, render=False)

            button = BUTTONS[self.connection.get_data()]
            self.emulation.button(button)
            self.emulation.tick(1, render=True)
            state.update(self.read_m)
            yield i, self.emulation.screen.ndarray.copy(), state.get_score()

    def read_hp(self, start):
        return 256 * self.read_m(start) + self.read_m(start + 1)

    def distance_from_start(self, x_pos, y_pos, map_):
        if map_ != 40:
            return 0
        return round(math.sqrt((x_pos - 4) ** 2 + (y_pos - 6) ** 2), 2)

    def safe_divide(self, a, b):
        try:
            return round(a / b, 2)
        except ZeroDivisionError:
            return None

    def read_m(self, addr):
        return self.emulation.memory[addr]
