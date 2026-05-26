import time
import json
from pathlib import Path
from movement_driver.movement_driver import MovementDriver

"""
This script runs a predefined movement plan based on coordinates
provided in location_map.json for MATRIX1 -> PLATE24.
It implements safe Z-height travel to prevent tip collisions.
"""

SLEEP_TIME = 1.5
SAFE_Z = 100.0
DIP_Z = 60.0
SPEED = 3000


def load_locations(file_path):
    """Loads the location map JSON file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not parse {file_path}. Invalid JSON.")
        return None


def main():
    # 1. Load the location map
    base_dir = Path(__file__).resolve().parent
    map_path = base_dir.parent / "location_map.json"  # <-- Added .parent here

    location_map = load_locations(map_path)
    if not location_map:
        return

    # Extract PLATE24 coordinates from MATRIX1
    try:
        plate24_coords = location_map["MATRIX1"]["PLATE24"]
    except KeyError as e:
        print(f"Error: Missing expected key in JSON map - {e}")
        return

    # 2. Initialize movement system
    print("Initializing movement system...")
    movement_system = MovementDriver()

    print("\nMoving to safe Z-height before starting sequence...")
    # Go to safe Z first before ANY XY movement. x=None, y=None ensures strictly vertical movement.
    movement_system.move(x=None, y=None, z=SAFE_Z, speed=SPEED)
    time.sleep(SLEEP_TIME)

    print("\nRunning predefined JSON matrix sequence...")

    try:
        # Iterate through rows (A, B, C, D)
        for row_name in sorted(plate24_coords.keys()):
            print(f"\n=== Processing Row {row_name} ===")
            row_points = plate24_coords[row_name]

            # Iterate through each [x, y] point in the current row
            for index, point in enumerate(row_points):
                x, y = point[0], point[1]
                print(f"Targeting {row_name}{index + 1} at X:{x}, Y:{y}")

                # 1. Move XY to the target coordinate (Z remains at SAFE_Z)
                movement_system.move(x=x, y=y, z=None, speed=SPEED)

                # 2. Move Z down to dip height (XY remains locked)
                movement_system.move(x=None, y=None, z=DIP_Z, speed=SPEED)
                time.sleep(SLEEP_TIME)  # Wait in the well

                # 3. Move Z back up to safe travel height (XY remains locked)
                movement_system.move(x=None, y=None, z=SAFE_Z, speed=SPEED)

                # Check hardware location after returning to safe height
                loc = movement_system.get_position()
                print(f"Position check (Safe Height): {loc}")

    except Exception as e:
        print(f"An error occurred during movement sequence: {e}")

    finally:
        print("\nSequence complete. Moving to safe Z before closing...")
        # Final safety measure: ensure Z is up before shutting down
        try:
            movement_system.move(x=None, y=None, z=SAFE_Z, speed=SPEED)
        except:
            pass

        print("Closing connection...")
        # The destructor handles resetting and closing the serial port
        del movement_system


if __name__ == "__main__":
    main()