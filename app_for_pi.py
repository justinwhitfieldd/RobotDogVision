from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
app = Flask(__name__)

rev_motor = 8  # IN1 on the relay board, physical pin 14
fire = 10  # IN2 on the relay board, physical pin 15
# Setup GPIO
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(rev_motor, GPIO.OUT) 
GPIO.setup(fire, GPIO.OUT)

# Initial state for relays
GPIO.output(rev_motor, GPIO.LOW)
GPIO.output(fire, GPIO.LOW)


def toggle_relay(pin, state):
    """Toggle the relay to the desired state (True for ON, False for OFF)."""
    GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

toggle_relay(rev_motor, True)
toggle_relay(fire, True)

@app.route('/rev_motor', methods=['POST'])
def rev_motor():
    toggle_relay(rev_motor, False)
    # Return a success response
    return jsonify({'status': 'success', 'message': 'shot fired'}), 200

@app.route('/stop_rev_motor', methods=['POST'])
def stop_rev_motor():
    toggle_relay(rev_motor, True)
    # Return a success response
    return jsonify({'status': 'success', 'message': 'shot fired'}), 200

@app.route('/shoot', methods=['POST'])
def shoot():

    toggle_relay(fire, False)
    time.sleep(0.3)
    toggle_relay(fire, True)
    # Return a success response
    return jsonify({'status': 'success', 'message': 'shot fired'}), 200

@app.route('/rev_and_shoot', methods=['POST'])
def rev_and_shoot():
    # Get JSON data from the request
    data = request.get_json()

    toggle_relay(rev_motor, False)
    time.sleep(1)
    toggle_relay(fire, False)
    time.sleep(0.3)
    toggle_relay(fire, True)
    toggle_relay(rev_motor, True)
    # Return a success response
    return jsonify({'status': 'success', 'message': 'shot fired'}), 200

if __name__ == '__main__':
    app.run(port=3002)  # Run on a different port since 3001 is used by the Node.js server
