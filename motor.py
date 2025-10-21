import RPi.GPIO as GPIO
import time
from enum import Enum

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
        GPIO.setup([self.x_step, self.x_dir, self.z_step, self.z_dir, self.en], GPIO.OUT)
        GPIO.output(self.en, GPIO.LOW)  # Enable drivers

    def move_motor(self, motor: Motor, direction: Direction, steps, step_delay=0.005):
        if motor == Motor.MotorCards:
            dir_pin = self.x_dir
            step_pin = self.x_step
        elif motor == Motor.MotorMagazin:
            dir_pin = self.z_dir
            step_pin = self.z_step
        else:
            raise ValueError("Motor must be MotorCards or MotorMagazin")
        GPIO.output(dir_pin, GPIO.HIGH if direction == Direction.Forward else GPIO.LOW)
        for _ in range(steps):
            GPIO.output(step_pin, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(step_pin, GPIO.LOW)
            time.sleep(step_delay)

    def cleanup(self):
        GPIO.output(self.en, GPIO.HIGH)  # Disable drivers
        GPIO.cleanup()

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
