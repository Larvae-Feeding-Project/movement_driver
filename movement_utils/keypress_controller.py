import time
import keyboard
from movement_driver.movement_driver import MovementDriver

# Define data structures and initial values
MOVEMENT_SLEEP_TIME = 5
current_loc = [50,50,50,3000]
step_sizes = [0.1, 1, 5, 10, 30, 50, 100]
step_size_index = 4

# Initialize movement system
movement_system = MovementDriver()
print("Initializing movement system...")
time.sleep(MOVEMENT_SLEEP_TIME)

movement_system.move(current_loc[0], current_loc[1], current_loc[2], current_loc[3])
print("Moving to location: " + str(current_loc))
while True:
    print("Press key...")
    event = keyboard.read_event()
    if event.event_type == keyboard.KEY_DOWN:
        print(f"Key pressed: {event.name}")
        if event.name == 'esc':
            break

        elif event.name == 'up':
            print("UP arrow pressed")
            try:
                current_loc[1] += step_sizes[step_size_index]
                movement_system.move(current_loc[0], current_loc[1], current_loc[2], current_loc[3])
            except:
                print("Error: out of bounds")

        elif event.name == 'down':
            print("DOWN arrow pressed")
            try:
                current_loc[1] -= step_sizes[step_size_index]
                movement_system.move(current_loc[0], current_loc[1], current_loc[2], current_loc[3])
            except:
                print("Error: out of bounds")

        elif event.name == 'left':
            print("LEFT arrow pressed")
            try:
                current_loc[0] += step_sizes[step_size_index]
                movement_system.move(current_loc[0], current_loc[1], current_loc[2], current_loc[3])
            except:
                print("Error: out of bounds")

        elif event.name == 'right':
            print("RIGHT arrow pressed")
            try:
                current_loc[0] -= step_sizes[step_size_index]
                movement_system.move(current_loc[0], current_loc[1], current_loc[2], current_loc[3])
            except:
                print("Error: out of bounds")

        elif event.name == 'u':
            if step_size_index + 1 < len(step_sizes):
                step_size_index += 1
            print("Step size changed to: " + str(step_sizes[step_size_index]))

        elif event.name == 'i':
            if step_size_index - 1 > -1:
                step_size_index -= 1
            print("Step size changed to: " + str(step_sizes[step_size_index]))

        elif event.name == 'a':
            print("A pressed")
            try:
                current_loc[2] += step_sizes[step_size_index]
                movement_system.move(current_loc[0], current_loc[1], current_loc[2], current_loc[3])
            except:
                print("Error: out of bounds")

        elif event.name == 'z':
            print("Z pressed")
            try:
                current_loc[2] -= step_sizes[step_size_index]
                movement_system.move(current_loc[0], current_loc[1], current_loc[2], current_loc[3])
            except:
                print("Error: out of bounds")





    time.sleep(MOVEMENT_SLEEP_TIME)