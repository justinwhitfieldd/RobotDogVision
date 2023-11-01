const io = require("socket.io-client");
const { Go1, Go1Mode } = require("@droneblocks/go1-js");

const FRAME_WIDTH = 640;
const FRAME_HEIGHT = 480;
const CENTER_THRESHOLD = 50;

let dog = new Go1();
dog.init();
dog.setMode(Go1Mode.walk);

const socket = io("http://192.168.137.27:5000"); // Replace localhost with your Flask server's IP

socket.on("center_point", async (centerX, centerY) => {
  const frameCenterX = FRAME_WIDTH / 2;
  const frameCenterY = FRAME_HEIGHT / 2;

  const dx = centerX - frameCenterX;
  const dy = centerY - frameCenterY;

  console.log(`Received center point: (${centerX}, ${centerY})`);

  if (Math.abs(dx) <= CENTER_THRESHOLD && Math.abs(dy) <= CENTER_THRESHOLD) {
    dog.setLedColor(255, 0, 0); // Set LED to red
    console.log("SHOOT");
  } else {
    dog.setLedColor(255, 255, 255); // Set LED to white

    if (Math.abs(dx) > CENTER_THRESHOLD) {
      await (dx > 0 ? dog.turnRight(0.1, 500) : dog.turnLeft(0.1, 500));
    }

    if (Math.abs(dy) > CENTER_THRESHOLD) {
      await (dy > 0 ? dog.lookDown(0.6, 500) : dog.lookUp(0.6, 500));
    }
  }
});

socket.on("dog_command", async (command) => {
  console.log("Received command from Flask:", command);
  
  switch (command) {
    case 'TURN_LEFT':
      await dog.turnLeft(0.1, 500);
      break;
    case 'TURN_RIGHT':
      await dog.turnRight(0.1, 500);
      break;
    case 'LOOK_UP':
      await dog.lookUp(0.6, 500);
      break;
    case 'LOOK_DOWN':
      await dog.lookDown(0.6, 500);
      break;
  }
});
