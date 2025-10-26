import time
import os
from motor import MotorController, Motor, Direction
from camera import create_camera
from image_ki import CardRecognizer
from carddata import CardData
from csv_out import write_carddata_csv
from gpio_manager import gpio  # Use our GPIO manager instead of direct RPi.GPIO

# === Default Configurable Constants ===
DEFAULT_MAGAZINE_SIZE = 70
DEFAULT_SEPARATE_STEPS = 200
DEFAULT_OUTPUT_STEPS = 200
DEFAULT_MAGAZINE_MOVE_STEPS = 100
DEFAULT_MAGAZINE_RETURN_STEPS = 7000
DEFAULT_IMAGE_DIR = "images"
DEFAULT_MAGAZIN_NAME = 'A'
DEFAULT_MOTOR_PINS = {'X_STEP': 17, 'X_DIR': 27, 'Z_STEP': 24, 'Z_DIR': 25, 'EN': 4}
DEFAULT_HOME_SENSOR_PIN = 21
# =====================================

class ProcessController:
    def __init__(self, magazine_size=DEFAULT_MAGAZINE_SIZE, separate_steps=DEFAULT_SEPARATE_STEPS, output_steps=DEFAULT_OUTPUT_STEPS, magazine_move_steps=DEFAULT_MAGAZINE_MOVE_STEPS, magazine_return_steps=DEFAULT_MAGAZINE_RETURN_STEPS, image_dir=DEFAULT_IMAGE_DIR, magazin_name=DEFAULT_MAGAZIN_NAME, motor_pins=None, home_sensor_pin=DEFAULT_HOME_SENSOR_PIN):
        self.magazine_size = magazine_size
        self.separate_steps = separate_steps
        self.output_steps = output_steps
        self.magazine_move_steps = magazine_move_steps
        self.magazine_return_steps = magazine_return_steps
        self.image_dir = image_dir
        self.magazin_name = magazin_name
        self.home_sensor_pin = home_sensor_pin
        if motor_pins is None:
            motor_pins = DEFAULT_MOTOR_PINS
        self.motor = MotorController(motor_pins['X_STEP'], motor_pins['X_DIR'], motor_pins['Z_STEP'], motor_pins['Z_DIR'], motor_pins['EN'])
        self.camera = create_camera()
        self.recognizer = CardRecognizer()
        os.makedirs(self.image_dir, exist_ok=True)
        gpio.setup(self.home_sensor_pin, gpio.IN)
        # runtime state
        self.current_position = 0
        self._stop_event = None
        self._thread = None
        self.on_card_processed = None  # Callback(card: CardData, position: int)

    def move_magazine_to_home(self, step_delay=0.005, max_steps=10000):
        steps = 0
        while gpio.input(self.home_sensor_pin) == gpio.LOW and steps < max_steps:
            self.motor.move_motor(Motor.MotorMagazin, Direction.Backward, 1, step_delay)
            steps += 1
        print(f"Magazine homed after {steps} steps.")

    def advance_magazine_positions(self, positions=1):
        """Advance the magazine forward by `positions` (each position uses magazine_move_steps)."""
        total_steps = positions * self.magazine_move_steps
        if total_steps > 0:
            self.motor.move_motor(Motor.MotorMagazin, Direction.Forward, total_steps)

    def run(self, home_magazine=False, start_index=1, magazin_name=None):
        """
        Run the processing loop synchronously.
        - home_magazine: if True, perform homing first
        - start_index: start processing from this magazine slot (1-based). If >1, homing will be skipped unless requested.
        - fachbuchstabe: override the fachbuchstabe for this run
        """
        if magazin_name is not None:
            self.magazin_name = magazin_name

        # Home logic: only run homing if requested and starting from first position
        if home_magazine and start_index == 1:
            self.move_magazine_to_home()

        # If starting from a later index, advance magazine to that slot
        if start_index > 1:
            # advance (start_index-1) positions
            self.advance_magazine_positions(start_index - 1)

        results: list[CardData] = []
        self.current_position = start_index - 1
        for i in range(start_index, self.magazine_size + 1):
            # 1. Motor: Separate card
            if self._stop_event is not None and self._stop_event.is_set():
                print("Stop requested before separating card. Exiting loop.")
                break
            self.motor.move_motor(Motor.MotorCards, Direction.Forward, self.separate_steps)
            # 2. Capture image
            image_timestamp = int(time.time())
            image_filename = f"image_{image_timestamp}.png"
            image_path = os.path.join(self.image_dir, image_filename)
            self.camera.capture(output_path=image_path, show_preview=False)
            # 3. Recognize card
            card: CardData = self.recognizer.recognize(image_path)
            # 4. Save CardData object for later CSV export
            # attach the image_path to the CardData so csv writer can use the filename
            card.image_path = image_path
            results.append(card)
            self.current_position = i
            # Notify about processed card
            if self.on_card_processed:
                self.on_card_processed(card, i)
            # 5. Motor: Output card (move forward)
            if self._stop_event is not None and self._stop_event.is_set():
                print("Stop requested after recognition. Attempting to cleanup and exit.")
                break
            self.motor.move_motor(Motor.MotorCards, Direction.Forward, self.output_steps)
            # 6. Motor: Move magazine (skip on last iteration)
            if i < self.magazine_size:
                self.motor.move_motor(Motor.MotorMagazin, Direction.Forward, self.magazine_move_steps)
                # update current position after magazine move
                self.current_position = i + 1
            print(f"Karte gelesen: {card}")
            
        
        if i == self.magazine_size:
            # Move magazine back to starting position after loop, but only if we finished the complete magazine
            print("Move: Return to start")
            self.motor.move_motor(Motor.MotorMagazin, Direction.Backward, self.magazine_return_steps)

        # self.motor.cleanup()
        # Save results to CSV using helper
        timestamp = int(time.time())
        csv_filename = f"single_magazin_{timestamp}.csv"
        csv_path = os.path.join(os.getcwd(), "csv", csv_filename)
        write_carddata_csv(results, csv_path, magazin_name=self.magazin_name, start_index=start_index)
        print(f"Prozess abgeschlossen. Ergebnisse gespeichert in {csv_path}")

    # --- Async control ---
    def start_async(self, home_magazine=False, start_index=1, magazin_name=None):
        """Start the process in a background thread. Returns the thread object."""
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Process already running")
        self._stop_event = __import__('threading').Event()
        def target():
            try:
                self.run(home_magazine=home_magazine, start_index=start_index, magazin_name=magazin_name)
            finally:
                # clear thread and event on exit
                self._stop_event = None
                self._thread = None
        self._thread = __import__('threading').Thread(target=target, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self, emergency=False):
        """Request the running process to stop. If emergency=True, attempt immediate motor cleanup."""
        if self._stop_event:
            self._stop_event.set()
        if emergency:
            try:
                self.motor.cleanup()
            except Exception as e:
                print(f"Error during emergency cleanup: {e}")

if __name__ == "__main__":
    gpio.setmode(gpio.BCM)
    controller = ProcessController()
    controller.run(home_magazine=True)
    controller.run(home_magazine=False)

