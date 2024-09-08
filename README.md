# IOT CHESSBOARD







## Communication protocol with Arduino Nano

The raspberry pi is communicating with the arduino nano using serial communication over a USB cable used for both power and serial com. 

To make the communication more robust, I've decided to create a communication protocol that works based on commands IDs. First 4 bits a command define the ID of the command which determines the parsing needed to understand the command. 



__From RASPBERRY PI TO ARDUINO :__


### _ID : 0001_ : 


**GOAL** : This command is used to set a range of LEDs to a specific color. The command works like this :

- First 4 bits is the ID of the command so `0001`
- Next 6 bits is the index of the start of the range of LEDs (`0-63`)
- Next 6 bits is the index of the end of the range of LEDS (`0-63`)
- Next 24 bits is the color the LEDs should be set to, (8 bits for RED, 8 bits for GREEN and 8 bits for BLUE)

### _ID : 0100_ : 


**GOAL** : This command is used to set leds that are not next to each other to a specific color. This command can only be used for **MAX 63 LEDS**. If you want to turn **ALL LEDs** on or off please use command ID 0001.


- First 4 bits is the ID of the command so `0100`
- Next 6 bits is the number of LEDs that this command contains (`0-63`) 
- Next 24 bits is the color the LEDs should be set to, (8 bits for RED, 8 bits for GREEN and 8 bits for BLUE)
- Then we have 6 bits per LED, based on the number of LED that this command has.


__From ARDUINO TO RASPBERRY PI :__
