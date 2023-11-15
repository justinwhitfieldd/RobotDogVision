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
    console.log('Received command:', command);

    switch (command) {
        case 'up':
            dog.lookUp(0.6, 500);
            break;
        case 'down':
            dog.lookDown(0.6, 500);
            break;
        case 'left':
            dog.turnLeft(0.1, 500);
            break;
        case 'right':
            dog.turnRight(0.1, 500);
            break;
    }

    res.send('Command received.');
});

app.listen(3000, () => {
    console.log('Node.js server running on port 3000.');
});
