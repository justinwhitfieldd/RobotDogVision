import RPi.GPIO as GPIO
import time

# Corrected pin definitions using BOARD numbering system
relay_pin1 = 8  # IN1 on the relay board, physical pin 14
relay_pin2 = 10  # IN2 on the relay board, physical pin 15
relay_pin3 = 12   # IN3 on the relay board, physical pin 18
relay_pin4 = 16  # IN4 on the relay board, physical pin 23
# Setup GPIO
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(relay_pin1, GPIO.OUT)  # Set relay pins to be an output
GPIO.setup(relay_pin2, GPIO.OUT)


# Initial state for relays
GPIO.output(relay_pin1, GPIO.LOW)
GPIO.output(relay_pin2, GPIO.LOW)

def toggle_relay(pin, state):
    """Toggle the relay to the desired state (True for ON, False for OFF)."""
    GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

try:
    # Main program loop
    while True:
        toggle_relay(relay_pin1, False)
        toggle_relay(relay_pin2, False)
        # Turn on relays one by one
        turd = input()
        if turd == "shoot":
            toggle_relay(relay_pin1, True)
            time.sleep(1)
            toggle_relay(relay_pin2, True)
            time.sleep(0.3)

except KeyboardInterrupt:
    # Clean up GPIO on CTRL+C exit
    GPIO.cleanup()

# Clean up GPIO on normal exit
GPIO.cleanup()