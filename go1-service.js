const express = require('express');
const bodyParser = require('body-parser');
const { Go1, Go1Mode } = require("@droneblocks/go1-js");

const app = express();

app.use(bodyParser.json());
let isMoving = false; // Flag to track if the robot is moving

let dog = new Go1();
dog.init();
dog.setMode(Go1Mode.walk);
// const centerX = 120;
// const centerY = 120;
let num = 0;

async function moveDogTowards(targetX, targetY, centerX, centerY) {
    if (isMoving) {
        console.log('Move in progress, waiting...');
        return; // Exit the function if a move is already in progress
      }
      isMoving = true; // Set the flag to indicate movement has started

    const xDifference = targetX - centerX;
    const yDifference = targetY - centerY;
    num = num + 1;
    // Threshold to determine if the dog should move
    const moveThreshold = 15; // Adjust this value based on your needs

    // Moving on the Y-axis (Up or Down)
    // if (Math.abs(yDifference) > moveThreshold) {
    //     if (yDifference < 0) {
    //         // Target is up
    //         console.log('Moving up');
    //         dog.lookUp(0.6, 1000); // Assuming lookUp is the correct method for moving forward
    //     } else {
    //         // Target is down
    //         console.log('Moving down');
    //         dog.lookDown(0.6, 1000); // Assuming lookDown is the correct method for moving backward
    //     }
    // }
    if (num % 10 == 0) {
        dog.resetBody();
    }
    if (Math.abs(xDifference) > moveThreshold) {
        dog.setMode(Go1Mode.walk);

        if (xDifference < 0) {
            // Target is to the left
            dog.resetBody();
            console.log('Moving left');
            dog.turnLeft(0.1, 0.5); // The speed and duration can be adjusted
        } else {
            // Target is to the right
            dog.resetBody();
            console.log('Moving right');
            dog.turnRight(0.1, 0.5);
        }
    } else {
        dog.resetBody();
    }
    isMoving = false; // Reset the flag once the movement is complete
}
app.post('/receive_command', (req, res) => {
    const x = req.body.center_x
    const y = req.body.center_y
    const center_x = req.body.image_center_x
    const center_y = req.body.image_center_y
    console.log('Received coordinates:', x, y, center_x, center_y);
    
    moveDogTowards(x, y, center_x, center_y);


    res.status(200).send('Coordinates received');
});

app.listen(3001, () => {
    console.log('Node.js server running on port 3001.');
});

