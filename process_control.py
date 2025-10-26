import time
import os
from motor import MotorController, Motor, Direction
from camera import PiCameraCapture
from image_ki import CardRecognizer
from carddata import CardData
import RPi.GPIO as GPIO

# === Default Configurable Constants ===
DEFAULT_MAGAZINE_SIZE = 70
DEFAULT_SEPARATE_STEPS = 200
DEFAULT_OUTPUT_STEPS = 200
DEFAULT_MAGAZINE_MOVE_STEPS = 100
DEFAULT_MAGAZINE_RETURN_STEPS = 7000
DEFAULT_IMAGE_DIR = "images"
DEFAULT_FACHBUCHSTABE = 'A'
DEFAULT_MOTOR_PINS = {'X_STEP': 17, 'X_DIR': 27, 'Z_STEP': 24, 'Z_DIR': 25, 'EN': 4}
DEFAULT_HOME_SENSOR_PIN = 21
# =====================================

class ProcessController:
    def __init__(self, magazine_size=DEFAULT_MAGAZINE_SIZE, separate_steps=DEFAULT_SEPARATE_STEPS, output_steps=DEFAULT_OUTPUT_STEPS, magazine_move_steps=DEFAULT_MAGAZINE_MOVE_STEPS, magazine_return_steps=DEFAULT_MAGAZINE_RETURN_STEPS, image_dir=DEFAULT_IMAGE_DIR, fachbuchstabe=DEFAULT_FACHBUCHSTABE, motor_pins=None, home_sensor_pin=DEFAULT_HOME_SENSOR_PIN):
        self.magazine_size = magazine_size
        self.separate_steps = separate_steps
        self.output_steps = output_steps
        self.magazine_move_steps = magazine_move_steps
        self.magazine_return_steps = magazine_return_steps
        self.image_dir = image_dir
        self.fachbuchstabe = fachbuchstabe
        self.home_sensor_pin = home_sensor_pin
        if motor_pins is None:
            motor_pins = DEFAULT_MOTOR_PINS
        self.motor = MotorController(motor_pins['X_STEP'], motor_pins['X_DIR'], motor_pins['Z_STEP'], motor_pins['Z_DIR'], motor_pins['EN'])
        self.camera = PiCameraCapture()
        self.recognizer = CardRecognizer()
        os.makedirs(self.image_dir, exist_ok=True)
        GPIO.setup(self.home_sensor_pin, GPIO.IN)

    def move_magazine_to_home(self, step_delay=0.005, max_steps=10000):
        steps = 0
        while GPIO.input(self.home_sensor_pin) == GPIO.LOW and steps < max_steps:
            self.motor.move_motor(Motor.MotorMagazin, Direction.Backward, 1, step_delay)
            steps += 1
        print(f"Magazine homed after {steps} steps.")

    def run(self, home_magazine=False):
        if home_magazine:
            self.move_magazine_to_home()

        results = []
        for i in range(1, self.magazine_size + 1):
            # 1. Motor: Separate card
            self.motor.move_motor(Motor.MotorCards, Direction.Forward, self.separate_steps)
            # 2. Capture image
            image_timestamp = int(time.time())
            image_filename = f"image_{image_timestamp}.png"
            image_path = os.path.join(self.image_dir, image_filename)
            self.camera.capture(output_path=image_path, show_preview=False)
            # 3. Recognize card
            card = self.recognizer.recognize(image_path)
            # 4. Save card data and position
            row = [
                self.fachbuchstabe,         # Fachbuchstabe
                str(i),                    # Fachnummer
                card.kartenname,           # Kartenname
                image_filename,            # Bildnummer
                card.edition,
                card.kartennummer,
                card.sprache,
                card.verlag,
                card.erscheinungsjahr,
                card.region,
                card.seltenheit,
                card.kartentyp,
                card.subtyp,
                card.farbe,
                card.spezialeffekte,
                card.limitierung,
                card.autogramm,
                card.memorabilia,
                card.zustand,
                "unbekannt",              # Ankaufspreis (not provided)
                card.marktwert             # Marktwert
            ]
            results.append(row)
            # 5. Motor: Output card (move forward)
            self.motor.move_motor(Motor.MotorCards, Direction.Forward, self.output_steps)
            # 6. Motor: Move magazine (skip on last iteration)
            if i < self.magazine_size:
                self.motor.move_motor(Motor.MotorMagazin, Direction.Forward, self.magazine_move_steps)
        # Move magazine back to starting position after loop
        self.motor.move_motor(Motor.MotorMagazin, Direction.Backward, self.magazine_return_steps)
        self.motor.cleanup()
        # Save results to CSV
        csv_header = [
            "Fachbuchstabe","Fachnummer","Kartenname","Bildnummer","Edition","Kartennummer","Sprache","Verlag","Erscheinungsjahr","Region","Seltenheit","Kartentyp","Subtyp","Farbe","Spezialeffekte","Limitierung","Autogramm","Memorabilia","Zustand","Ankaufspreis","Marktwert"
        ]
        timestamp = int(time.time())
        csv_filename = f"{timestamp}_Magazin.csv"
        csv_path = os.path.join(os.getcwd(), csv_filename)
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(";".join(csv_header) + "\n")
            for row in results:
                f.write(";".join(row) + "\n")
        print(f"Prozess abgeschlossen. Ergebnisse gespeichert in {csv_path}")

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    controller = ProcessController()
    controller.run(home_magazine=True)
    controller.run(home_magazine=False)

