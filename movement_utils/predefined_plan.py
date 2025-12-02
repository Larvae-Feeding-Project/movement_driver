import time
import serial

PORT = 'COM7'   # your printer port
BAUD = 250000

# ---------------------------
# LIST OF PREDEFINED G-CODES
# ---------------------------
gcode_list = [
    "M115",               # firmware info
    "G28",                # home all axes
    # === Y = 150 ===
    "G0 X100 Y150 Z50 F3000",
    "G0 X100 Y150 Z30 F3000",
    "G0 X100 Y150 Z50 F3000",

    "G0 X112 Y150 Z50 F3000",
    "G0 X112 Y150 Z30 F3000",
    "G0 X112 Y150 Z50 F3000",

    "G0 X124 Y150 Z50 F3000",
    "G0 X124 Y150 Z30 F3000",
    "G0 X124 Y150 Z50 F3000",

    "G0 X136 Y150 Z50 F3000",
    "G0 X136 Y150 Z30 F3000",
    "G0 X136 Y150 Z50 F3000",

    "G0 X148 Y150 Z50 F3000",
    "G0 X148 Y150 Z30 F3000",
    "G0 X148 Y150 Z50 F3000",

    "G0 X160 Y150 Z50 F3000",
    "G0 X160 Y150 Z30 F3000",
    "G0 X160 Y150 Z50 F3000",

    # === Y = 162 ===
    "G0 X100 Y162 Z50 F3000",
    "G0 X100 Y162 Z30 F3000",
    "G0 X100 Y162 Z50 F3000",

    "G0 X112 Y162 Z50 F3000",
    "G0 X112 Y162 Z30 F3000",
    "G0 X112 Y162 Z50 F3000",

    "G0 X124 Y162 Z50 F3000",
    "G0 X124 Y162 Z30 F3000",
    "G0 X124 Y162 Z50 F3000",

    "G0 X136 Y162 Z50 F3000",
    "G0 X136 Y162 Z30 F3000",
    "G0 X136 Y162 Z50 F3000",

    "G0 X148 Y162 Z50 F3000",
    "G0 X148 Y162 Z30 F3000",
    "G0 X148 Y162 Z50 F3000",

    "G0 X160 Y162 Z50 F3000",
    "G0 X160 Y162 Z30 F3000",
    "G0 X160 Y162 Z50 F3000",

    # === Y = 174 ===
    "G0 X100 Y174 Z50 F3000",
    "G0 X100 Y174 Z30 F3000",
    "G0 X100 Y174 Z50 F3000",

    "G0 X112 Y174 Z50 F3000",
    "G0 X112 Y174 Z30 F3000",
    "G0 X112 Y174 Z50 F3000",

    "G0 X124 Y174 Z50 F3000",
    "G0 X124 Y174 Z30 F3000",
    "G0 X124 Y174 Z50 F3000",

    "G0 X136 Y174 Z50 F3000",
    "G0 X136 Y174 Z30 F3000",
    "G0 X136 Y174 Z50 F3000",

    "G0 X148 Y174 Z50 F3000",
    "G0 X148 Y174 Z30 F3000",
    "G0 X148 Y174 Z50 F3000",

    "G0 X160 Y174 Z50 F3000",
    "G0 X160 Y174 Z30 F3000",
    "G0 X160 Y174 Z50 F3000",

    # === Y = 186 ===
    "G0 X100 Y186 Z50 F3000",
    "G0 X100 Y186 Z30 F3000",
    "G0 X100 Y186 Z50 F3000",

    "G0 X112 Y186 Z50 F3000",
    "G0 X112 Y186 Z30 F3000",
    "G0 X112 Y186 Z50 F3000",

    "G0 X124 Y186 Z50 F3000",
    "G0 X124 Y186 Z30 F3000",
    "G0 X124 Y186 Z50 F3000",

    "G0 X136 Y186 Z50 F3000",
    "G0 X136 Y186 Z30 F3000",
    "G0 X136 Y186 Z50 F3000",

    "G0 X148 Y186 Z50 F3000",
    "G0 X148 Y186 Z30 F3000",
    "G0 X148 Y186 Z50 F3000",

    "G0 X160 Y186 Z50 F3000",
    "G0 X160 Y186 Z30 F3000",
    "G0 X160 Y186 Z50 F3000",

    # === Y = 198 ===
    "G0 X100 Y198 Z50 F3000",
    "G0 X100 Y198 Z30 F3000",
    "G0 X100 Y198 Z50 F3000",

    "G0 X112 Y198 Z50 F3000",
    "G0 X112 Y198 Z30 F3000",
    "G0 X112 Y198 Z50 F3000",

    "G0 X124 Y198 Z50 F3000",
    "G0 X124 Y198 Z30 F3000",
    "G0 X124 Y198 Z50 F3000",

    "G0 X136 Y198 Z50 F3000",
    "G0 X136 Y198 Z30 F3000",
    "G0 X136 Y198 Z50 F3000",

    "G0 X148 Y198 Z50 F3000",
    "G0 X148 Y198 Z30 F3000",
    "G0 X148 Y198 Z50 F3000",

    "G0 X160 Y198 Z50 F3000",
    "G0 X160 Y198 Z30 F3000",
    "G0 X160 Y198 Z50 F3000",

    # === Y = 210 ===
    "G0 X100 Y210 Z50 F3000",
    "G0 X100 Y210 Z30 F3000",
    "G0 X100 Y210 Z50 F3000",

    "G0 X112 Y210 Z50 F3000",
    "G0 X112 Y210 Z30 F3000",
    "G0 X112 Y210 Z50 F3000",

    "G0 X124 Y210 Z50 F3000",
    "G0 X124 Y210 Z30 F3000",
    "G0 X124 Y210 Z50 F3000",

    "G0 X136 Y210 Z50 F3000",
    "G0 X136 Y210 Z30 F3000",
    "G0 X136 Y210 Z50 F3000",

    "G0 X148 Y210 Z50 F3000",
    "G0 X148 Y210 Z30 F3000",
    "G0 X148 Y210 Z50 F3000",

    "G0 X160 Y210 Z50 F3000",
    "G0 X160 Y210 Z30 F3000",
    "G0 X160 Y210 Z50 F3000",

    #"G0 X0 Y0 F3000",     # return to origin
    "M114"                # report position
]

print(f"Connecting to {PORT} at {BAUD} baud...")
ser = serial.Serial(PORT, BAUD, timeout=1)

# Many printer boards reset on serial connect
time.sleep(2)

def send(cmd: str):
    print(f">> {cmd}")
    ser.write((cmd + "\n").encode())
    ser.flush()
    while True:
        resp = ser.readline().decode("ascii", errors="ignore").strip()
        if resp:
            print("<<", resp)
        if resp == "ok" or resp == "":
            break

print("Connected!")
print("Running predefined G-code sequence...\n")

try:
    for cmd in gcode_list:
        send(cmd)
        time.sleep(1.5)

finally:
    print("\nDone. Closing connection...")
    ser.close()