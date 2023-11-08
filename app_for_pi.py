from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
app = Flask(__name__)

relay_pin1 = 8  # IN1 on the relay board, physical pin 14
relay_pin2 = 10  # IN2 on the relay board, physical pin 15
relay_pin3 = 12   # IN3 on the relay board, physical pin 18
relay_pin4 = 16  # IN4 on the relay board, physical pin 23
# Setup GPIO
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(relay_pin1, GPIO.OUT)  # Set relay pins to be an output
GPIO.setup(relay_pin2, GPIO.OUT)
GPIO.setup(relay_pin3, GPIO.OUT)
GPIO.setup(relay_pin4, GPIO.OUT)

# Initial state for relays
GPIO.output(relay_pin1, GPIO.LOW)
GPIO.output(relay_pin2, GPIO.LOW)
GPIO.output(relay_pin3, GPIO.LOW)
GPIO.output(relay_pin4, GPIO.LOW)

def toggle_relay(pin, state):
    """Toggle the relay to the desired state (True for ON, False for OFF)."""
    GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

toggle_relay(relay_pin1, True)
toggle_relay(relay_pin4, True)
toggle_relay(relay_pin3, False)
toggle_relay(relay_pin2, True)

@app.route('/receive_command', methods=['POST'])
def receive_command():
    # Get JSON data from the request
    data = request.get_json()

    toggle_relay(relay_pin1, False)
    toggle_relay(relay_pin4, False)
    toggle_relay(relay_pin3, True)
    toggle_relay(relay_pin2, False)
    time.sleep(3)
    toggle_relay(relay_pin1, True)
    toggle_relay(relay_pin4, True)
    toggle_relay(relay_pin3, False)
    toggle_relay(relay_pin2, True)

    # Return a success response
    return jsonify({'status': 'success', 'message': 'shot fired'}), 200

if __name__ == '__main__':
    app.run(port=3002)  # Run on a different port if 3001 is used by the Node.js server
