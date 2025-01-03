from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import time
from os import mkdir

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk



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

GRID_ROWS = 2
GRID_COLUMNS = 3
INDEX_MAPPING = {
    "episode": (0, 0),
    "natbag": (0, 1),
    "mars": (0, 2),
    "e": (1, 0),
    "sqrt_2": (1, 1),
    "genome": (1, 2)
}

# Thread-safe queue for images
image_queue = Queue()


class ImageGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Image Grid")

        # Create a grid of labels
        self.labels = []
        for row in range(GRID_ROWS):
            row_labels = []
            for col in range(GRID_COLUMNS):
                label = ttk.Label(self.root, text="", borderwidth=2, relief="solid")
                label.grid(row=row, column=col, padx=5, pady=5)
                row_labels.append(label)
            self.labels.append(row_labels)

        # Start the periodic image update loop
        self.update_images()

    def update_images(self):
        while not image_queue.empty():
            # Get image and position from the queue
            row, col, img = image_queue.get()
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLUMNS:
                # Display the image in the appropriate label
                photo = ImageTk.PhotoImage(img)
                self.labels[row][col].configure(image=photo)
                self.labels[row][col].image = photo

        # Schedule the next update
        self.root.after(100, self.update_images)


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
        # img.save(PATH_FORMAT_STRING.format(name=a[0],frame=a[1][0]))
        image_queue.put((INDEX_MAPPING[a[0]][0], INDEX_MAPPING[a[0]][1], img))


def main():
    root = tk.Tk()
    app = ImageGridApp(root)

    with ThreadPoolExecutor(16) as pool:
        q = Queue()
        futures = [pool.submit(emulate, src, URL[src], q, True) for src in URL]
        rend_future = pool.submit(render, q)
        root.mainloop()

    return 0


if __name__ == "__main__":
    main()
