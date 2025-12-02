import time
import serial
import json


class MovementDriver:

    def __init__(self):

        # Open relevant printer data
        try:
            with open('data.json', 'r') as file:
                self.movement_data = json.load(file)
        except FileNotFoundError:
            print('No movement data file found')
        except Exception as e:
            print("Exception occurred")

        # Open serial with the movement system
        try:
            self.COMPORT, self.BAUD_RATE = self.movement_data['COMPORT'], self.movement_data['BAUD_RATE']
            print(f"Connecting to {self.COMPORT} at {self.BAUD_RATE} baud...")
            self.movement_ser = serial.Serial(self.COMPORT, self.BAUD_RATE, timeout=1)
        except Exception as e:
            print("Movement system connection error")

        self.reset()

    def __del__(self):
        """
        Movement system destructor. Resets the system and closes the serial port
        :return:
        """
        # Close movement serial
        self.reset()
        self.movement_ser.close()

    def reset(self):
        """
        Resets the movement system, which means moving it to (0,0,0) and resetting relative location
        :return:
        """
        self._send_command("G28")

    """Need to implement the string refactoring"""
    def move(self, x='', y='', z='', speed=3000):
        self._send_command("G0 X100 Y150 Z50 F3000")

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
