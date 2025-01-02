from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import time
from os import mkdir

from PIL import Image

import emulation

URL = {
    "episode": "http://10.10.10.33:8000/episode",
    "natbag": "http://10.10.10.33:8000/natbag",
    "mars": "http://10.10.10.33:8000/mars",
    "e": "http://10.10.10.33:8000/e",
    "sqrt_2": "http://10.10.10.33:8000/sqrt_2",
    "genome": "http://10.10.10.33:8000/genome",
}

PATH_FORMAT_STRING = "./images/{name}/{frame}.png"


def emulate(name, url, q: Queue, use=False):
    try:
        mkdir(f"./images/{name}/")
    except:
        pass
    game = emulation.GameEmulation(url)
    start = time()
    frames = 0
    for i in game.run():
        frames += i[0]
        if use:
            print(f"game {name}, {i[2]}")
            q.put_nowait((name, i))
        print(f"fps={frames / (time()-start)}")


def render(q: Queue):
    while True:
        a = q.get()
        img = Image.fromarray(a[1][1])
        img.save(PATH_FORMAT_STRING.format(name=a[0],frame=a[1][0]))


def main():
    with ThreadPoolExecutor(16) as pool:
        q = Queue()
        futures = [pool.submit(emulate, src, URL[src], q, True) for src in URL]
        rend_future = pool.submit(render, q)

    return 0


if __name__ == "__main__":
    main()
