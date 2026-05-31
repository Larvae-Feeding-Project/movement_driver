import time
import re
from pathlib import Path
import serial
import json


def load_json(file_path):
    """
        Loads json files and returns them
        :param file_path: path to json file
        :return: data structure inside the json if success otherwise returns None
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not parse {file_path}. Invalid JSON.")
        return None


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
        map_path = base_dir / "location_map.json"

        # Open printer data dict
        self.movement_data = load_json(data_path)

        # Open location map data
        self.location_map = load_json(map_path)

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

    def set_injection_temperature(self, temperature):
        """
        Sets the temperature of the injection system (arm heating)
        :param temperature: temperature in degrees Celsius
        :return:
        """

    def move(self, x=None, y=None, z=None, speed=3000):
        """
        Move to specific location. If an axis is not specified, the location on that axis will not change
        :param x: x coordinate (float)
        :param y: y coordinate (float)
        :param z: z coordinate (float)
        :param speed: speed of movement (float)
        :return: True if moved successfully (including ack of end of movement), else otherwise
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
        if x is not None: parts.append(f"X{x}")
        if y is not None: parts.append(f"Y{y}")
        if z is not None: parts.append(f"Z{z}")
        parts.append(f"F{speed}")

        try:
            self._send_command(" ".join(parts))

            # Make sure the arm is in place before return True
            # Send M400, which receives OK only after finished moving
            print(">> Waiting for hardware buffer to clear (M400)...")
            self._send_command("M400")
            return True
        except Exception as e:
            print(">> Movement Error!")
            return False

        # maybe verify location with get_position

    def move_to_well(self, matrix, plate_type, row, col, z = 100, speed = 3000):
        """
            Move to specified well position
        :param matrix: matrix the well is in ("MATRIX1", "MATRIX2", "MATRIX3")
        :param plate_type: plate of 24 or 48 wells ("PLATE48", "PLATE24")
        :param row: row of the well
        :param col: col of the well
        :return: True if moved successfully (including ack of end of movement), else otherwise
        """
        if matrix not in ["MATRIX1", "MATRIX2", "MATRIX3"]:
            print("Invalid matrix name")
            return False
        if plate_type not in ["PLATE48", "PLATE24"]:
            print("Invalid plate name")
            return False

        # Add more validity checks later

        x, y = self.location_map[matrix][plate_type][row][col]
        return self.move(x, y, z, speed)


    def get_position(self):
        """
            Return the current position of the movement system
            :return: tuple of the location (x,y,z) or None if it fails
        """
        max_retries = 5
        retries = 0

        while retries < max_retries:
            rx_lst = self._send_command("M114")

            # Check if we got enough data
            if len(rx_lst) >= 2:
                loc_str = rx_lst[-2]

                # Extract x, y, z values
                match = re.search(
                    r'X:(-?\d+(?:\.\d+)?)\s+Y:(-?\d+(?:\.\d+)?)\s+Z:(-?\d+(?:\.\d+)?)', loc_str, re.IGNORECASE)

                if match:
                    x, y, z = map(float, match.groups())
                    return x, y, z

            # If we reached here, something went wrong. Increment and wait.
            retries += 1
            print(f"Warning: Failed to get position. Retry {retries}/{max_retries}...")
            time.sleep(0.5)  # Give the hardware/buffer a moment to clear

        return False

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
