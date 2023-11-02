const express = require('express');
const bodyParser = require('body-parser');
const { Go1, Go1Mode } = require("@droneblocks/go1-js");

const app = express();

app.use(bodyParser.json());

let dog = new Go1();
dog.init();
dog.setMode(Go1Mode.walk);

app.post('/receive_command', (req, res) => {
  const command = req.body.command;
  const intensity = req.body.intensity;
  const duration = req.body.duration;

  console.log(`Received command: ${command}, intensity: ${intensity}, duration: ${duration}ms`);

  switch (command) {
      case 'up':
          dog.lookUp(intensity, duration);
          break;
      case 'down':
          dog.lookDown(intensity, duration);
          break;
      case 'left':
          dog.turnLeft(intensity, duration);
          break;
      case 'right':
          dog.turnRight(intensity, duration);
          break;
  }

  res.send('Command received.');
});

app.listen(3000, () => {
    console.log('Node.js server running on port 3000.');
});
