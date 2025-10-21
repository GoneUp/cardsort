import RPi.GPIO as GPIO
import time

# Pin configuration
X_STEP = 17
X_DIR = 27

Z_STEP = 24
Z_DIR = 25
EN = 4

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup([X_STEP, X_DIR, Z_STEP, Z_DIR, EN], GPIO.OUT)

# Enable drivers (LOW = enabled)
GPIO.output(EN, GPIO.LOW)


print("enable done")
# Move X Axis
GPIO.output(X_DIR, GPIO.HIGH)  # or GPIO.LOW to reverse
for _ in range(2000):  # 200 steps = ~1 revolution
    GPIO.output(X_STEP, GPIO.HIGH)
    time.sleep(0.008)
    GPIO.output(X_STEP, GPIO.LOW)
    time.sleep(0.008)

print("x done")
# Short delay between axis moves
time.sleep(0.5)

# Move Z Axis
GPIO.output(Z_DIR, GPIO.HIGH)  # or GPIO.HIGH
for _ in range(2000):
    GPIO.output(Z_STEP, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(Z_STEP, GPIO.LOW)
    time.sleep(0.001)

print("z done");
# Disable drivers (optional)
GPIO.output(EN, GPIO.HIGH)
GPIO.cleanup()