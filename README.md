# Movement System

This repo contains our implementation of the movement system. 
It includes the movement system driver, its local data, and a few 
examples and utils that can be used for calibration.

## Dependencies

1. pySerial
2. keyboard
3. time
4. serial
5. json
6. pathlib

## Utils
Utils can be found in the movement_utils folder. They can be used for calibration, introduction of new commands and more. The current utils are:
1. command_sender: initiates the movement system, and then enable the user to send G-code directly to the movement_system.
2. predefined_plan: moves the movement system in a pre-built plan. Can be modified for different needs and scenarios.
3. keypress_controller: Creates a keyboard press based interface with the movement system. Useful for calibration. WORK IN PROGRESS, NOT VALIDATED YET

## Usage
IN THE FUTURE WILL BE USED BY CONTROL UNIT


## Contributing

Asaf Shahar and Nitai Gildor
