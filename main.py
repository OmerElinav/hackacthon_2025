from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import time
from os import mkdir

from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2



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
REVERSE_INDEX = {
    (0, 0): "episode",
    (0, 1): "natbag" ,
    (0, 2): "mars",
    (1, 0): "e",
    (1, 1): "sqrt_2",
    (1, 2): "genome"
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
                label = ttk.Label(self.root, text=REVERSE_INDEX[(row, col)], borderwidth=2, relief="solid")
                label.grid(row=row, column=col, padx=5, pady=5)
                row_labels.append(label)
            self.labels.append(row_labels)

        # Start the periodic image update loop
        self.update_images()

    def update_images(self):
        while not image_queue.empty():
            # Get image and position from the queue
            row, col, img, text = image_queue.get()
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLUMNS:
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype("arial.ttf", 50)
                text_position = (img.width - 50, img.height - 50)  # Bottom-right corner
                text_position = (text_position[0] - len(text) * 25, text_position[1] - 45)  # Adjust for text width
                draw.text(text_position, text, fill="green", font=font)

                # Display the image in the appropriate label
                photo = ImageTk.PhotoImage(img)
                self.labels[row][col].configure(image=photo)
                self.labels[row][col].image = photo

        # Schedule the next update
        self.root.after(100, self.update_images)


# Add text to ndarray image
def add_text_to_ndarray(image, text):
    cv2.putText(image, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (144, 144, 144), 2, cv2.LINE_AA)
    return image

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
            #print(f"game {name}, {i[2]}")
            q.put_nowait((name, i))
        #print(f"fps={frames / (time()-start)}")


def render(q: Queue):
    # Grid settings
    grid_size = (2, 3)  # 1x3 grid
    cell_size = (480, 480)  # Size of each grid cell
    canvas_size = (grid_size[0] * cell_size[0], grid_size[1] * cell_size[1])
    # Create a blank canvas
    canvas = np.zeros((canvas_size[0], canvas_size[1], 3), dtype=np.uint8)
    x = 0
    while True:
        x += 1
        a = q.get()
        #img = Image.fromarray(a[1][1])
        #(width, height) = (round(img.width * 3), round(img.height * 2.5))
        #im_resized = img.resize((width, height))
        # img.save(PATH_FORMAT_STRING.format(name=a[0],frame=a[1][0]))
        #image_queue.put((INDEX_MAPPING[a[0]][0], INDEX_MAPPING[a[0]][1], im_resized, f"{a[0]}: {a[1][2]}"))
        i, j = INDEX_MAPPING[a[0]]
        cv_image = cv2.cvtColor(a[1][1], cv2.COLOR_RGBA2BGR)
        cv_image = cv2.resize(cv_image, cell_size)  # Resize to fit the cell
        cv_image = add_text_to_ndarray(cv_image, f"{a[0]}: {a[1][2]}")
        x, y = i * cell_size[0], j * cell_size[1]
        canvas[x:x + cell_size[0], y:y + cell_size[1]] = cv_image
        cv2.imshow("Dynamic Grid", canvas)
        cv2.waitKey(1)



def main():
    root = tk.Tk()
    #app = ImageGridApp(root)

    with ThreadPoolExecutor(16) as pool:
        q = Queue()
        futures = [pool.submit(emulate, src, URL[src], q, True) for src in URL]
        rend_future = pool.submit(render, q)
        #root.mainloop()

    return 0


if __name__ == "__main__":
    main()
