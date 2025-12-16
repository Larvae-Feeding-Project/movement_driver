import time
from movement_driver.movement_driver import MovementDriver


movement_system = MovementDriver()


try:
    while True:
        cmd = input(">> ").strip()
        if cmd.lower() in ("exit", "quit"):
            break
        if cmd == "":
            continue
        movement_system._send_command(cmd) # Private func used here purposefully
        time.sleep(2)

finally:
    movement_system.__del__()