import time
import re
from pathlib import Path
import serial
import json


class MovementDriver:

    def __init__(self):
        """
        Movement system constructor. opens local movement data (comport, bounds etc) or receives them from control system
        (TO BE IMPLEMENTED). Finally sets the injection tip temperature (TO BE IMPLEMENTED) and resets the positions.
        :return: MovementDriver object
        """
        # Path to movement module directory
        base_dir = Path(__file__).resolve().parent
        data_path = base_dir / "movement_data.json"

        # Open printer data dict
        try:
            with open(data_path, "r") as file:
                self.movement_data = json.load(file)
            print("Movement data loaded")
        except FileNotFoundError:
            print('No movement data file found')
        except Exception as e:
            print("Exception occurred, could not open data.json")

        # Load movement system bounds
        self.XLIMIT, self.YLIMIT, self.ZLIMIT = \
            self.movement_data['XLIMIT'], self.movement_data['YLIMIT'], self.movement_data['ZLIMIT']
        print("Loaded system bounds")

        # Open serial with the movement system
        try:
            self.COMPORT, self.BAUD_RATE = self.movement_data['COMPORT'], self.movement_data['BAUD_RATE']
            print(f"Connecting to {self.COMPORT} at {self.BAUD_RATE} baud...")
            self.movement_ser = serial.Serial(self.COMPORT, self.BAUD_RATE, timeout=1)
        except Exception as e:
            print("Movement system connection error")

        # Reset system
        self.reset()
        time.sleep(3)

    def __del__(self):
        """
        Movement system destructor. Resets the system and closes the serial port
        :return: VOID
        """
        # Close movement serial
        self.reset()
        time.sleep(4)
        self.movement_ser.close()

    def reset(self):
        """
        Resets the movement system, which means moving it to (0,0,0) and resetting relative location
        :return: VOID
        """
        print("Resetting movement system")
        self._send_command("G28")

    def move(self, x=None, y=None, z=None, speed=3000):
        """
        Move to specific location. If an axis is not specified, the location on that axis will not change
        :param x: x coordinate (float)
        :param y: y coordinate (float)
        :param z: z coordinate (float)
        :param speed: speed of movement (float)
        :return: VOID
        """
        # Validate coordinates only if provided
        if x is not None:
            if x < 0 or x > self.XLIMIT:
                raise Exception("Invalid X movement command")

        if y is not None:
            if y < 0 or y > self.YLIMIT:
                raise Exception("Invalid Y movement command")

        if z is not None:
            if z < 0 or z > self.ZLIMIT:
                raise Exception("Invalid Z movement command")

        # Movement command list
        parts = ["G0"]

        if x is not None:
            parts.append(f"X{x}")
        if y is not None:
            parts.append(f"Y{y}")
        if z is not None:
            parts.append(f"Z{z}")

        parts.append(f"F{speed}")
        self._send_command(" ".join(parts))

    def get_position(self):
        """
        Return the current position of the movement system
        :return: tuple of the location (x,y,z)
        """

        # Loops until getting a location
        while True:
            # Make sure the return list actually has location data
            rx_lst = self._send_command("M114")
            if len(rx_lst) < 2:
                continue
            loc_str = rx_lst[-2]  # Returns the location string

            # Extract x, y, z values
            match = re.search(
                r'X:(-?\d+(?:\.\d+)?)\s+Y:(-?\d+(?:\.\d+)?)\s+Z:(-?\d+(?:\.\d+)?)', loc_str
            )
            if match:
                break

        x, y, z = map(float, match.groups())
        return x, y, z

    def _send_command(self, command):
        """
        Sends a command to the movement system
        :param command: String of the command to be sent to the movement system
        :return: list of the responses the movement system sent back (until ok)
        """
        # Encode and send the command to the movement system
        print(">> Sending command: " + str(command))
        self.movement_ser.write((command + "\n").encode())
        self.movement_ser.flush()

        # Read and save all responses until an "ok" or empty line
        self.movement_ser.reset_input_buffer()
        resp_lst = []
        while True:
            resp = self.movement_ser.readline().decode("ascii", errors="ignore").strip()
            print("<<", resp)  # In the future change to log!!!
            resp_lst.append(resp)

            # Received acknowledgement
            if resp == "ok" or resp == "" or resp == " ok":
                break

        return resp_lst
