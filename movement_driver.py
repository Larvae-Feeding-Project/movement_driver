import time
import serial
import json


class MovementDriver:

    def __init__(self):

        # Open printer data dict
        try:
            with open('data.json', 'r') as file:
                self.movement_data = json.load(file)
        except FileNotFoundError:
            print('No movement data file found')
        except Exception as e:
            print("Exception occurred, could not open data.json")

        # Load movement system bounds
        self.XLIMIT, self.YLIMIT, self.ZLIMIT = \
            self.movement_data['XLIMIT'], self.movement_data['YLIMIT'], self.movement_data['ZLIMIT']

        # Open serial with the movement system
        try:
            self.COMPORT, self.BAUD_RATE = self.movement_data['COMPORT'], self.movement_data['BAUD_RATE']
            print(f"Connecting to {self.COMPORT} at {self.BAUD_RATE} baud...")
            self.movement_ser = serial.Serial(self.COMPORT, self.BAUD_RATE, timeout=1)
        except Exception as e:
            print("Movement system connection error")

        # Reset system
        self.reset()

    def __del__(self):
        """
        Movement system destructor. Resets the system and closes the serial port
        :return: VOID
        """
        # Close movement serial
        self.reset()
        self.movement_ser.close()

    def reset(self):
        """
        Resets the movement system, which means moving it to (0,0,0) and resetting relative location
        :return: VOID
        """
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

    """
    Need to check how to receive and present the position
    """
    def get_position(self):
        self._send_command("M114")

    """
    Need to analyze how to loop responses are built
    """
    def _send_command(self, command):
        # Encode and send the command to the movement system
        self.movement_ser.write((command + "\n").encode())
        self.movement_ser.flush()

        # Read and print all responses until an "ok" or empty line
        while True:
            resp = self.movement_ser.readline().decode("ascii", errors="ignore").strip()
            if resp:
                print("<<", resp)
            if resp == "ok" or resp == "":
                break
