import random
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from dataclasses import dataclass, fields

import math



def read_hp(start):
     return 256 * read_m(start) + read_m(start + 1)

LEVELS_ADDR = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]
COORDS_ADDR = [0xD362, 0xD361, 0xD35E]
HP_ADDR = [(0xD16C, 0xD18D), (0xD198, 0xD1B9), (0xD1C4, 0xD1E5), (0xD1F0, 0xD211), (0xD21C, 0xD23D), (0xD248, 0xD269)]
BADGES_ADDR = 0xD356

def distance_from_start(x_pos, y_pos, map_):
     if map_ != 40:
          return 0
     return round(math.sqrt((x_pos - 4)**2 + (y_pos - 6)**2), 2)



def safe_divide(a, b):
     try:
          return round(a / b, 2)
     except ZeroDivisionError:
          return None

@dataclass
class GameState:
     levels: list[int] = None
     visited_regions: set = None
     visited_regions_count: int = 0
     badges: str = None


     def update(self):
          if self.visited_regions is None:
               self.visited_regions = set()
          self.levels = [read_m(a) for a in LEVELS_ADDR]
          self.badges = read_m(BADGES_ADDR)
          coords = [read_m(a) for a in COORDS_ADDR]
          map_ = coords[2]
          self.visited_regions.add(map_)
          self.visited_regions_count = len(self.visited_regions)

pyboy = PyBoy("pokemon_red.gb",  window="null")
pyboy.set_emulation_speed(0)
pokemon = pyboy.game_wrapper
pokemon.start_game()
pyboy.tick(5)

buttons = [
     "a",  "b", "start", "select", "left", "right", "up", "down"
]


def read_m(addr):
     return pyboy.memory[addr]

i = 0
button = None
state = GameState()
while True:
     i += 1
     button = random.choice(buttons)
     pyboy.button(button)
     pyboy.tick(render=i % 1500 == 0)

     if i % 15000 == 0:
          state.update()
          try:
               pyboy.screen.image.save(f"images/last_frame_{i}.png")
               print(state)
          except:
               pass


pyboy.stop(save=False)







