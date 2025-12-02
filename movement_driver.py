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

    def __del__(self):
        # Close movement serial
        self.movement_ser.close()

    #def reset(self):
