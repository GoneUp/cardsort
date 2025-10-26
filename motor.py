import time
from enum import Enum
from gpio_manager import gpio

class Motor(Enum):
    MotorCards = 'x'
    MotorMagazin = 'z'

class Direction(Enum):
    Forward = 'forward'
    Backward = 'backward'

class MotorController:
    def __init__(self, x_step, x_dir, z_step, z_dir, en):
        self.x_step = x_step
        self.x_dir = x_dir
        self.z_step = z_step
        self.z_dir = z_dir
        self.en = en
        for pin in [self.x_step, self.x_dir, self.z_step, self.z_dir, self.en]:
            gpio.setup(pin, gpio.OUT)
        gpio.output(self.en, gpio.LOW)  # Enable drivers

    def move_motor(self, motor: Motor, direction: Direction, steps, step_delay=0.005):
        if motor == Motor.MotorCards:
            dir_pin = self.x_dir
            step_pin = self.x_step
        elif motor == Motor.MotorMagazin:
            dir_pin = self.z_dir
            step_pin = self.z_step
        else:
            raise ValueError("Motor must be MotorCards or MotorMagazin")
        gpio.output(dir_pin, gpio.HIGH if direction == Direction.Forward else gpio.LOW)
        for _ in range(steps):
            gpio.output(step_pin, gpio.HIGH)
            time.sleep(step_delay)
            gpio.output(step_pin, gpio.LOW)
            time.sleep(step_delay)

    def cleanup(self):
        gpio.output(self.en, gpio.HIGH)  # Disable drivers
        gpio.cleanup()

if __name__ == "__main__":
    # Demo usage
    X_STEP = 17
    X_DIR = 27
    Z_STEP = 24
    Z_DIR = 25
    EN = 4
    motor = MotorController(X_STEP, X_DIR, Z_STEP, Z_DIR, EN)
    print("Moving MotorCards forward 1000 steps...")
    motor.move_motor(Motor.MotorCards, Direction.Forward, 1000)
    print("Moving MotorMagazin backward 500 steps...")
    motor.move_motor(Motor.MotorMagazin, Direction.Backward, 500)
    motor.cleanup()
    print("Done.")
