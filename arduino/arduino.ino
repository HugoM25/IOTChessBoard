#include <FastLED.h>

#define BOARD_SIZE 8
#define LED_PIN 6
#define NUM_LEDS 64
#define DEBOUNCE_CHECKS 5  // Number of checks to confirm a change

CRGB leds[NUM_LEDS];

int rowpins[BOARD_SIZE] = {11, 12, A0, A1, A2, A3, A4, A5}; // set row pin numbers
int columnpins[BOARD_SIZE] = {10,9,8,7,5,4,3,2}; // set column pins
int board[BOARD_SIZE * BOARD_SIZE]; // array for pin read value
int lastBoardState[BOARD_SIZE * BOARD_SIZE]; // store the last stable state
int debounceCounter[BOARD_SIZE * BOARD_SIZE]; // track how many times a change has been observed
int lastSentBoardState[BOARD_SIZE * BOARD_SIZE]; // store the last sent state

bool boardChanged = false; // Flag to indicate if the board state has changed

void setup() {
  Serial.begin(9600); // Start serial comms
  delay(2000);
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50);
  InitializePinsReed(); // initialise function
  InitializeBoardState(); // Initialize lastBoardState, lastSentBoardState, and debounceCounter arrays
}

void loop() {
  // Check for and process any incoming LED commands
  ReadCommands();

  // Read the reed switch matrix and handle debouncing
  readReedMatrix();
  
  // Send the board matrix data only if there was a confirmed change
  if (boardChanged) {
    SendBoardViaSerial();
    boardChanged = false; // Reset the flag after sending
  }
}

// Function to initialize the PINS needed for the reed switch matrix
void InitializePinsReed() {
  for (int i = 0; i < BOARD_SIZE; i++) { 
    pinMode(rowpins[i], INPUT_PULLUP);
    digitalWrite(rowpins[i], LOW);
  }

  for (int j = 0; j < BOARD_SIZE; j++) { 
    pinMode(columnpins[j], INPUT);
    digitalWrite(columnpins[j], HIGH);
  }
}

// Function to initialize the board state, lastSentBoardState, and debounce counters
void InitializeBoardState() {
  for (int i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
    lastBoardState[i] = 0;
    lastSentBoardState[i] = 0;
    debounceCounter[i] = 0;
  }
}

void readReedMatrix() {
  for (int i = 0; i < BOARD_SIZE; i++) {
    pinMode(rowpins[i], OUTPUT); // set row to LOW OUTPUT
    for (int j = 0; j < BOARD_SIZE; j++) {
      int currentState = !digitalRead(columnpins[j]);
      int index = j * BOARD_SIZE + i;

      // Check for changes and debounce
      if (currentState != lastBoardState[index]) {
        debounceCounter[index]++;
        if (debounceCounter[index] >= DEBOUNCE_CHECKS) {
          if (board[index] != currentState) {
            board[index] = currentState;
            boardChanged = true; // Mark that a change has occurred
          }
          lastBoardState[index] = currentState;
          debounceCounter[index] = 0; // Reset counter after confirming the change
        }
      } else {
        debounceCounter[index] = 0; // Reset counter if state remains the same
      }
    }
    pinMode(rowpins[i], INPUT_PULLUP); // set row back to INPUT
    digitalWrite(rowpins[i], LOW);
  }
  delay(50); // Adjust this delay as needed
}

void SendBoardViaSerial() {
    String boardData = "0101";  // Command ID for sending board data
    for (int i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        boardData += String(board[i]);
    }
    // Ensure the data is exactly 64 bits long
    while (boardData.length() < 64) {
        boardData += '0'; // Pad with zeros if needed
    }
    Serial.print(boardData + ';');
}

void ReadCommands(){
  // Check if there is incoming data from the computer
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil(';'); // Read incoming data until a ; character

    int command_id = strtol(data.substring(0, 4).c_str(), nullptr, 2);
    
    if (command_id == 1 ){
      int start_index = strtol(data.substring(4, 10).c_str(), nullptr, 2);
      int end_index = strtol(data.substring(10, 16).c_str(), nullptr, 2);
      int r = strtol(data.substring(17, 24 ).c_str(), nullptr, 2);
      int g = strtol(data.substring(24, 32 ).c_str(), nullptr, 2);
      int b = strtol(data.substring(32, 40 ).c_str(), nullptr, 2);

      for (int i = start_index; i <= end_index; i++) {
        if (i >= 0 && i < NUM_LEDS) {
          leds[i] = CRGB(r, g, b);
        }
      }
      FastLED.show(); // Update the LEDs
      SendAck();
    }
    else if (command_id == 4 ){
      int length = strtol(data.substring(4, 10).c_str(), nullptr, 2);
      int r = strtol(data.substring(10, 18 ).c_str(), nullptr, 2);
      int g = strtol(data.substring(18, 26 ).c_str(), nullptr, 2);
      int b = strtol(data.substring(26, 34 ).c_str(), nullptr, 2);

      int index_led = 100;
      int st = 34; 
      for (int i = 0; i< length; i++){
        index_led = strtol(data.substring(st, st+6).c_str(), nullptr, 2);
        leds[index_led] = CRGB(r,g,b); 
        st += 6; 
      }
      FastLED.show(); // Update the LEDs
      SendAck();
    }
    else if (command_id == 6){
      SendAck(); 
      SendBoardViaSerial(); 
    }
    else if (command_id == 9){
      // This is a test command to see if is working
      SendAck(); 
    }

    // Check the ID of the command 
  }
}


void SendAck(){
  // Send acknowledgement to RPI 
  Serial.print("1111;");
}

