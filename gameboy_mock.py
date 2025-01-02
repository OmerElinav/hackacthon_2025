import cv2
from PIL import Image

import emulation

size = 144, 160
fps = 60
out = cv2.VideoWriter(
    "output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (size[1], size[0]), True
)


game = emulation.GameEmulation("http://10.10.10.33:8000/episode")
x = 60 * 60 * 60 * 4
for i in game.run():
    x -= 1
    print(x)
    if x == 0:
        break

out.release()
