import serial
import time
import fastapi
import threading
from fastapi import HTTPException

# Serial port configuration
SELIAL_PORT = '/dev/cu.usbmodem1301'
arduino = serial.Serial(port=SELIAL_PORT, baudrate=9600, timeout=.1)

# Global dictionary to store controls
controls = {}

# FastAPI app instance
app = fastapi.FastAPI()

# Function to read data from serial and update global controls


def print_serial():
    global controls
    while True:
        data = arduino.readline()[:-2]  # Remove newline characters
        if not data:
            continue
        try:
            # Assuming the data format is 'name: value'
            name, value = data.decode("utf-8").split(": ")
            controls[name] = int(value)  # Store the value as integer
        except ValueError:
            # If the data can't be split correctly, skip this iteration
            print(f"Invalid data: {data}")

# FastAPI endpoint to get the value of a control by its name


@app.get("/controls/{name}")
def get_control(name: str):
    # Check if the control exists
    if name in controls:
        return {"data": controls[name]}
    else:
        raise HTTPException(status_code=404, detail="Control not found")

# Start the serial reading in a separate thread


def start_serial_thread():
    serial_thread = threading.Thread(target=print_serial, daemon=True)
    serial_thread.start()


# Start the FastAPI server and serial thread
if __name__ == "__main__":
    start_serial_thread()  # Start serial reading in the background
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
