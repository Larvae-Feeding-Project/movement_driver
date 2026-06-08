import sys
import time
import json
from pathlib import Path

# --- Path Configuration ---
# Calculate the absolute path to the project root (3 levels up from this file)
# Hierarchy: ROOT / movement_driver / movement_utils / predefined_callibrated.py
current_file = Path(__file__).resolve()
root_dir = current_file.parent.parent.parent
sys.path.append(str(root_dir))

# Now we can safely import from our custom modules
from movement_driver.movement_driver import MovementDriver
from fluidics_system.fluidics_module import FluidicsDriver

# --- Configuration Constants ---
SLEEP_TIME = 1.0
SAFE_Z = 100.0
DIP_Z = 57.0
SPEED = 3000
DISPENSE_AMOUNT_UL = 1000.0  # Amount to dispense per well in micro-liters


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
    # 1. Load the location map (assumed to be in the root directory)
    base_dir = Path(__file__).resolve().parent
    map_path = base_dir.parent / "location_map.json"  # <-- Added .parent here

    location_map = load_locations(map_path)
    if not location_map:
        return

    # Extract PLATE24 coordinates from MATRIX1
    try:
        plate24_coords = location_map["MATRIX3"]["PLATE24"]
    except KeyError as e:
        print(f"Error: Missing expected key in JSON map - {e}")
        return

    # 2. Initialize Subsystems
    print("Initializing movement system...")
    movement_system = MovementDriver()

    print("Initializing fluidics system...")
    fluidics_system = FluidicsDriver()

    try:
        # Move to safe Z before doing anything else
        print("\nMoving to safe Z-height...")
        movement_system.move(x=None, y=None, z=SAFE_Z, speed=SPEED)
        time.sleep(SLEEP_TIME)

        # IMPORTANT: In the real system, you might want to move to the EMPTY_CONTAINER_LOC
        # before calling fill_tube() so you don't drip on the deck.
        print("\nPriming the fluidics tube...")
        if not fluidics_system.fill_tube():
            print("Failed to prime tube. Aborting sequence.")
            return

        print("\n=== Starting Matrix Dispense Sequence ===")

        # Iterate through rows (A, B, C, D)
        for row_name in sorted(plate24_coords.keys()):
            print(f"\n--- Processing Row {row_name} ---")
            row_points = plate24_coords[row_name]

            # Iterate through each [x, y] point in the current row
            for index, point in enumerate(row_points):
                x, y = point[0], point[1]
                well_id = f"{row_name}{index + 1}"
                print(f"Targeting {well_id} at X:{x}, Y:{y}")

                # 1. Move XY to the target coordinate (Z remains at SAFE_Z)
                movement_system.move(x=x, y=y, z=None, speed=SPEED)

                # 2. Move Z down to dip height (XY remains locked)
                movement_system.move(x=None, y=None, z=DIP_Z, speed=SPEED)
                time.sleep(0.5)  # Brief pause to let hardware settle

                # 3. Dispense Fluid
                print(f"  -> Dispensing {DISPENSE_AMOUNT_UL}uL into {well_id}...")
                dispense_success = fluidics_system.output(DISPENSE_AMOUNT_UL)
                if not dispense_success:
                    print(f"  -> WARNING: Dispense failed at {well_id}")

                time.sleep(0.5)  # Brief pause to allow last drop to fall

                # 4. Move Z back up to safe travel height (XY remains locked)
                movement_system.move(x=None, y=None, z=SAFE_Z, speed=SPEED)

    except Exception as e:
        print(f"\nAn error occurred during sequence: {e}")

    finally:
        print("\n=== Sequence complete. Running Teardown ===")

        # Ensure Z is up to avoid collisions on the way back
        try:
            movement_system.move(x=None, y=None, z=SAFE_Z, speed=SPEED)
        except:
            pass

        print("Clearing fluidics tube...")
        fluidics_system.clear_tube()

        print("Shutting down connections...")
        # Destructors handle the hardware teardown
        del movement_system
        del fluidics_system
        print("Done.")


if __name__ == "__main__":
    main()