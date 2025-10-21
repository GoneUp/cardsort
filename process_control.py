import time
import os
from motor import MotorController, Motor, Direction
from camera import PiCameraCapture
from image_ki import CardRecognizer
from carddata import CardData

# Configurable parameters
MAGAZINE_SIZE = 70  # Number of cards to process (default 70)
X_STEP = 17
X_DIR = 27
Z_STEP = 24
Z_DIR = 25
EN = 4
SEPARATE_STEPS = 200  # Steps to separate a card
OUTPUT_STEPS = 200    # Steps to output a card
MAGAZINE_MOVE_STEPS = 100  # Steps to move magazine

IMAGE_DIR = "images"
FACHBUCHSTABE = 'A'
MAGAZINE_RETURN_STEPS = 7000  # Steps to return magazine to start (configurable)

os.makedirs(IMAGE_DIR, exist_ok=True)

motor = MotorController(X_STEP, X_DIR, Z_STEP, Z_DIR, EN)
camera = PiCameraCapture()
recognizer = CardRecognizer()

results = []


for i in range(1, MAGAZINE_SIZE + 1):
    # 1. Motor: Separate card
    motor.move_motor(Motor.MotorCards, Direction.Forward, SEPARATE_STEPS)
    # 2. Capture image
    image_timestamp = int(time.time())
    image_filename = f"image_{image_timestamp}.png"
    image_path = os.path.join(IMAGE_DIR, image_filename)
    camera.capture(output_path=image_path, show_preview=False)
    # 3. Recognize card
    card = recognizer.recognize(image_path)
    # 4. Save card data and position
    row = [
        FACHBUCHSTABE,         # Fachbuchstabe
        str(i),                # Fachnummer
        card.kartenname,       # Kartenname
        image_filename,        # Bildnummer
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
        "unbekannt",          # Ankaufspreis (not provided)
        card.marktwert         # Marktwert
    ]
    results.append(row)
    # 5. Motor: Output card (move forward)
    motor.move_motor(Motor.MotorCards, Direction.Forward, OUTPUT_STEPS)
    # 6. Motor: Move magazine (skip on last iteration)
    if i < MAGAZINE_SIZE:
        motor.move_motor(Motor.MotorMagazin, Direction.Forward, MAGAZINE_MOVE_STEPS)

# Move magazine back to starting position after loop
motor.move_motor(Motor.MotorMagazin, Direction.Backward, MAGAZINE_RETURN_STEPS)

motor.cleanup()

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
