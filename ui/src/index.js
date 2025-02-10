/**
 * Author: Michael Hadley, mikewesthad.com
 * Asset Credits:
 *  - Tuxemon, https://github.com/Tuxemon/Tuxemon
 */

const config = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: "game-container",
  pixelArt: true,
  physics: {
    default: "arcade",
    arcade: {
      gravity: { y: 0 },
    },
  },
  scene: {
    preload: preload,
    create: create,
    update: update,
  },
};

const game = new Phaser.Game(config);
let cursors;
let player;
let player2;
let showDebug = false;
let dialogueBox;
let dialogueText;
let isNearPlayer2;
let isTyping = false;
let currentMessage = '';

// Add these with other global variables at the top
let npcStartPosition;
let npcEndPosition;
let npcDirection = 1; // 1 for moving to end point, -1 for returning
let npcTimer;
let npcIsMoving = false;
const NPC_SPEED = 50;
const PAUSE_DURATION = 3000; // 3 seconds pause at each end

// Add this with other global variables at the top
let isInDialogue = false;

// Add this with other global variables at the top
const API_URL = 'http://localhost:8000';

async function sendMessageToAPI(message) {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message , philosopher_id: "descartes" })
    });
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    const data = await response.json();
    return data.response; // Assuming your API returns { response: "some text" }
  } catch (error) {
    console.error('Error:', error);
    return "Sorry, I'm having trouble responding right now.";
  }
}

function preload() {
  // Load multiple tilesets
  this.load.image("greece-tiles", "../assets/tilesets/ancient_greece_tileset.png");
  this.load.image("dirt-tiles", "../assets/tilesets/dirt.png");
  this.load.image("forest-tiles", "../assets/tilesets/forest.png");
  this.load.image("grass-tiles", "../assets/tilesets/grass.png");
  this.load.image("water-tiles", "../assets/tilesets/water.png");
  
  // Load tilemap
  this.load.tilemapTiledJSON("map", "../assets/tilemaps/ancient_greece_town.json");
  
  // Load both atlases
  this.load.atlas("atlas", "../assets/miguel/atlas.png", "../assets/miguel/atlas.json");
  this.load.atlas("descartes", "../assets/descartes/atlas.png", "../assets/descartes/atlas.json");
}

function create() {
  const map = this.make.tilemap({ key: "map" });

  // Add multiple tilesets
  const greeceTileset = map.addTilesetImage("ancient_greece_tileset", "greece-tiles");
  const dirtTileset = map.addTilesetImage("dirt", "dirt-tiles");
  const forestTileset = map.addTilesetImage("forest_tiles", "forest-tiles");
  const grassTileset = map.addTilesetImage("grass", "grass-tiles");
  const waterTileset = map.addTilesetImage("water", "water-tiles");

  // Create layers using multiple tilesets
  const belowLayer = map.createLayer("Below Player", [greeceTileset, dirtTileset, forestTileset, grassTileset, waterTileset], 0, 0);
  const worldLayer = map.createLayer("World", [greeceTileset, dirtTileset, forestTileset, grassTileset, waterTileset], 0, 0);
  const aboveLayer = map.createLayer("Above Player", [greeceTileset, dirtTileset, forestTileset, grassTileset, waterTileset], 0, 0);

  worldLayer.setCollisionByProperty({ collides: true });

  // By default, everything gets depth sorted on the screen in the order we created things. Here, we
  // want the "Above Player" layer to sit on top of the player, so we explicitly give it a depth.
  // Higher depths will sit on top of lower depth objects.
  aboveLayer.setDepth(10);

  // Object layers in Tiled let you embed extra info into a map - like a spawn point or custom
  // collision shapes. In the tmx file, there's an object layer with a point named "Spawn Point"
  const spawnPoint = map.findObject("Objects", (obj) => obj.name === "Spawn Point");
  const socratesSpawnPoint = map.findObject("Objects", (obj) => obj.name === "Socrates");
  const aristotleSpawnPoint = map.findObject("Objects", (obj) => obj.name === "Aristotle");
  const platoSpawnPoint = map.findObject("Objects", (obj) => obj.name === "Plato");

  // Create both players at the spawn point
  player = this.physics.add
    .sprite(spawnPoint.x, spawnPoint.y, "atlas", "miguel-front")
    .setSize(30, 40)
    .setOffset(0, 24);

  // Set NPC patrol points (adjust these coordinates as needed for your map)
  npcStartPosition = { x: 400, y: 300 }; // Starting position
  npcEndPosition = { x: 600, y: 300 };   // End position of patrol

  // Create NPC at the start position instead of near player
  player2 = this.physics.add
    .sprite(npcStartPosition.x, npcStartPosition.y, "descartes", "descartes-front")
    .setSize(30, 40)
    .setOffset(0, 24)
    .setImmovable(true);

  // Initialize NPC movement timer
  npcTimer = this.time.addEvent({
    delay: PAUSE_DURATION,
    callback: startNPCMovement,
    callbackScope: this,
    loop: true
  });

  // Add colliders for both players
  this.physics.add.collider(player, worldLayer);
  this.physics.add.collider(player, player2);

  // Create the player's walking animations from the texture atlas. These are stored in the global
  // animation manager so any sprite can access them.
  const anims = this.anims;
  anims.create({
    key: "miguel-left-walk",
    frames: anims.generateFrameNames("atlas", {
      prefix: "miguel-left-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });
  anims.create({
    key: "miguel-right-walk", 
    frames: anims.generateFrameNames("atlas", {
      prefix: "miguel-right-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });
  anims.create({
    key: "miguel-front-walk",
    frames: anims.generateFrameNames("atlas", {
      prefix: "miguel-front-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });
  anims.create({
    key: "miguel-back-walk",
    frames: anims.generateFrameNames("atlas", {
      prefix: "miguel-back-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });

  // Create animations for Descartes
  anims.create({
    key: "descartes-left-walk",
    frames: anims.generateFrameNames("descartes", {
      prefix: "descartes-left-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });
  anims.create({
    key: "descartes-right-walk",
    frames: anims.generateFrameNames("descartes", {
      prefix: "descartes-right-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });
  anims.create({
    key: "descartes-front-walk",
    frames: anims.generateFrameNames("descartes", {
      prefix: "descartes-front-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });
  anims.create({
    key: "descartes-back-walk",
    frames: anims.generateFrameNames("descartes", {
      prefix: "descartes-back-walk-",
      end: 9,
      zeroPad: 4,
    }),
    frameRate: 10,
    repeat: -1,
  });

  const camera = this.cameras.main;
  camera.startFollow(player);
  camera.setBounds(0, 0, map.widthInPixels, map.heightInPixels);

  cursors = this.input.keyboard.createCursorKeys();

  // Help text that has a "fixed" position on the screen
  // this.add
  //   .text(16, 16, 'Arrow keys to move\nPress "D" to show hitboxes', {
  //     font: "18px monospace",
  //     fill: "#000000",
  //     padding: { x: 20, y: 10 },
  //     backgroundColor: "#ffffff",
  //   })
  //   .setScrollFactor(0)
  //   .setDepth(30);

  // Debug graphics
  this.input.keyboard.once("keydown-D", (event) => {
    // Turn on physics debugging to show player's hitbox
    this.physics.world.createDebugGraphic();

    // Create worldLayer collision graphic above the player, but below the help text
    const graphics = this.add.graphics().setAlpha(0.75).setDepth(20);
    worldLayer.renderDebug(graphics, {
      tileColor: null, // Color of non-colliding tiles
      collidingTileColor: new Phaser.Display.Color(243, 134, 48, 255), // Color of colliding tiles
      faceColor: new Phaser.Display.Color(40, 39, 37, 255), // Color of colliding face edges
    });
  });

  // Calculate maximum height that won't exceed screen
  const maxDialogueHeight = 200; // This will show about 5-6 lines
  const screenPadding = 20;
  const dialogueY = this.game.config.height - maxDialogueHeight - screenPadding;

  dialogueBox = this.add
    .rectangle(400, dialogueY + (maxDialogueHeight/2), 700, maxDialogueHeight, 0x000000, 0.7)
    .setScrollFactor(0)
    .setDepth(30)
    .setVisible(false);

  dialogueText = this.add
    .text(60, dialogueY + screenPadding, '', {
      font: "18px monospace",
      fill: "#ffffff",
      padding: { x: 20, y: 10 },
      wordWrap: { width: 680 },
      lineSpacing: 6,
      maxLines: 5 // Limit visible lines
    })
    .setScrollFactor(0)
    .setDepth(30)
    .setVisible(false);

  this.input.keyboard.on('keydown-SPACE', () => {
    if (isNearPlayer2 && !isTyping) {  // Only open dialogue if not already typing
        // Open dialogue to start typing
        dialogueBox.setVisible(true);
        dialogueText.setVisible(true);
        isTyping = true;
        currentMessage = '';
        dialogueText.setText('Type your message: ');
        dialogueText.setColor('#00ff00');
        isInDialogue = true;  // This will make NPC stop and face player
        
        // Make NPC face the player immediately when starting dialogue
        if (player.x < player2.x) {
          player2.setTexture("atlas", "miguel-left");
        } else if (player.x > player2.x) {
          player2.setTexture("atlas", "miguel-right");
        } else if (player.y < player2.y) {
          player2.setTexture("atlas", "miguel-back");
        } else {
          player2.setTexture("atlas", "miguel-front");
        }
        
        // Stop any ongoing NPC movement
        npcIsMoving = false;
        player2.anims.stop();
    }
  });

  this.input.keyboard.on('keydown', async (event) => {
    if (!isTyping) return;

    if (event.key === 'Enter') {
      if (currentMessage.trim() !== '') {
        // Send message to API and wait for response
        dialogueText.setText('...');  // Show loading indicator
        dialogueText.setColor('#ffffff');
        
        const apiResponse = await sendMessageToAPI(currentMessage);
        
        // Show API response
        dialogueText.setText(apiResponse);
        dialogueText.setColor('#ffffff');
        
        currentMessage = '';
        isTyping = false;
        // Keep isInDialogue true so NPC stays facing player
      } else if (dialogueText.text !== 'Type your message: ') {
        // Reset to typing mode after reading NPC response
        dialogueText.setText('Type your message: ');
        dialogueText.setColor('#00ff00');
      }
    } else if (event.key === 'Escape') {
      dialogueBox.setVisible(false);
      dialogueText.setVisible(false);
      isTyping = false;
      currentMessage = '';
      isInDialogue = false;  // Allow NPC to resume movement
    } else if (event.key === 'Backspace') {
      currentMessage = currentMessage.slice(0, -1);
      dialogueText.setText('Type your message: ' + currentMessage);
      dialogueText.setColor('#00ff00');
    } else if (event.key.length === 1) { // Single character keys
      currentMessage += event.key;
      dialogueText.setText('Type your message: ' + currentMessage);
      dialogueText.setColor('#00ff00');
    }
  });
}

function startNPCMovement() {
  npcIsMoving = !npcIsMoving;
  
  if (npcIsMoving) {
    // Change NPC direction based on current position
    if (player2.x === npcStartPosition.x) {
      npcDirection = 1;
      player2.setTexture("descartes", "descartes-right");
    } else if (player2.x === npcEndPosition.x) {
      npcDirection = -1;
      player2.setTexture("descartes", "descartes-left");
    }
  }
}

function update(time, delta) {
  const speed = 175;
  const prevVelocity = player.body.velocity.clone();

  // Stop any previous movement from the last frame
  player.body.setVelocity(0);
  player2.body.setVelocity(0);

  // Horizontal movement
  if (cursors.left.isDown) {
    player.body.setVelocityX(-speed);
  } else if (cursors.right.isDown) {
    player.body.setVelocityX(speed);
  }

  // Vertical movement
  if (cursors.up.isDown) {
    player.body.setVelocityY(-speed);
  } else if (cursors.down.isDown) {
    player.body.setVelocityY(speed);
  }

  // Normalize and scale the velocity so that player can't move faster along a diagonal
  player.body.velocity.normalize().scale(speed);

  // Update the animation last and give left/right animations precedence over up/down animations
  if (cursors.left.isDown) {
    player.anims.play("miguel-left-walk", true);
  } else if (cursors.right.isDown) {
    player.anims.play("miguel-right-walk", true);
  } else if (cursors.up.isDown) {
    player.anims.play("miguel-back-walk", true);
  } else if (cursors.down.isDown) {
    player.anims.play("miguel-front-walk", true);
  } else {
    player.anims.stop();

    // If we were moving, pick and idle frame to use
    if (prevVelocity.x < 0) player.setTexture("atlas", "miguel-left");
    else if (prevVelocity.x > 0) player.setTexture("atlas", "miguel-right");
    else if (prevVelocity.y < 0) player.setTexture("atlas", "miguel-back");
    else if (prevVelocity.y > 0) player.setTexture("atlas", "miguel-front");
  }

  // Handle NPC movement
  if (npcIsMoving) {
    const targetX = npcDirection === 1 ? npcEndPosition.x : npcStartPosition.x;
    const distance = Math.abs(player2.x - targetX);

    if (distance > 1) {
      // Move NPC
      player2.x += NPC_SPEED * npcDirection * (delta / 1000);
      
      // Play walking animation
      if (npcDirection === 1) {
        player2.anims.play("descartes-right-walk", true);
      } else {
        player2.anims.play("descartes-left-walk", true);
      }
    } else {
      // Snap to exact position when close enough
      player2.x = targetX;
      player2.anims.stop();
      npcIsMoving = false;
    }
  } else {
    // Stop animation when not moving
    player2.anims.stop();
  }

  // Check if player is near player2 and update dialogue availability
  const distance = Phaser.Math.Distance.Between(
    player.x, player.y,
    player2.x, player2.y
  );
  isNearPlayer2 = distance < 100;

  if (isInDialogue) {
    // Stop NPC movement and face the player during dialogue
    npcIsMoving = false;
    player2.anims.stop();
    
    // Continuously update NPC facing direction to follow player
    if (player.x < player2.x) {
      player2.setTexture("descartes", "descartes-left");
    } else if (player.x > player2.x) {
      player2.setTexture("descartes", "descartes-right");
    } else if (player.y < player2.y) {
      player2.setTexture("descartes", "descartes-back");
    } else {
      player2.setTexture("descartes", "descartes-front");
    }
  } else {
    // Resume normal patrol behavior when not in dialogue
    if (!isNearPlayer2) {
      if (npcIsMoving) {
        const targetX = npcDirection === 1 ? npcEndPosition.x : npcStartPosition.x;
        const distance = Math.abs(player2.x - targetX);

        if (distance > 1) {
          // Move NPC
          player2.x += NPC_SPEED * npcDirection * (delta / 1000);
          
          // Play walking animation
          if (npcDirection === 1) {
            player2.anims.play("descartes-right-walk", true);
          } else {
            player2.anims.play("descartes-left-walk", true);
          }
        } else {
          // Snap to exact position when close enough
          player2.x = targetX;
          player2.anims.stop();
          npcIsMoving = false;
        }
      }
    }
  }

  // Disable player movement while typing
  if (isTyping) {
    player.body.setVelocity(0);
    return;
  }
}