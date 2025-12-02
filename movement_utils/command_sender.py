import time
import serial

PORT = 'COM7'   # <-- change this to your real COM port
BAUD = 250000

print(f"Connecting to {PORT} at {BAUD} baud...")
ser = serial.Serial(PORT, BAUD, timeout=1)

# many 3D printer boards reset when serial port opens
time.sleep(2)


def send(cmd: str):
    ser.write((cmd + "\n").encode())
    ser.flush()
    # read and print all responses until an "ok" or empty line
    while True:
        resp = ser.readline().decode("ascii", errors="ignore").strip()
        if resp:
            print("<<", resp)
        if resp == "ok" or resp == "":
            break

print("Connected!")
print("Type G-code commands (e.g., G28, G0 X100 Y100).")
print("Type 'exit' or 'quit' to close.\n")

try:
    while True:
        cmd = input(">> ").strip()
        if cmd.lower() in ("exit", "quit"):
            break
        if cmd == "":
            continue
        send(cmd)

finally:
    print("Closing connection...")
    ser.close()