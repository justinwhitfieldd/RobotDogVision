from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.form.get('command')
    print(f'Sending command: {command}')

    url = 'http://localhost:3000/receive_command'
    data = {'command': command}
    
    response = requests.post(url, json=data)
    
    return f'Command sent, Node.js responded with: {response.text}'

if __name__ == '__main__':
    app.run(port=5000)
