# ESP32-OSC2CV

Sending control voltage to synthesizers via OSC

Based on an idea by Jan Fiess

* <https://www.youtube.com/watch?v=GKnuqrTxj9k&ab_channel=janfiess>
* <https://github.com/janfiess/NodeMCU_OSC>

Using the OSC library from <https://github.com/CNMAT/OSC> and
TouchOSC from Hexler.net (<https://hexler.net/touchosc-mk1>). I still
use the old ("MK1") version of TouchOSC.

## TouchOSC layout file

I have restricted the x and y values of the sliders and the X/Y Pad from 0 to 255. I
use the values from x and y directly for ```dacWrite()``` which takes
input values from 0 to 255.

You can use the TouchOSC Editor (<https://hexler.net/touchosc-mk1#resources>) to modify the layout file.

### Page 1: Push Button

Page 1 of the TouchOSC layout consinsts of a single push putton. Pressing the push button on page 1 triggers pin 2 on the ESP32. This is the internal LED. This can be used as a quick connection test. But this can also be used to trigger an envelope generator or drum module by connecing pin 2 to the gate input of a synthesiser module.

### Page 2: X/Y Pad

Page 2 consists of an X/Y Pad.
The values of x and y will be sent to pin 25 and 26 which are the DAC (digital-analog-converter) pins of the ESP32. The output voltage can be sent to CV input connectors of synthesizers. For example to change the pitch of an oscillator or to open/close a filter.

### Page 3: Sliders and Push Buttons

You can find two sliders and two push buttons on page 3 of the TouchOSC layout. The value of slider 1 (the slider on the left hand side) is sent to pin 25. Slider 2 is connected to pin 26. The first push button sends a trigger to pin 32. The second push button sends a trigger to pin 33.

## Python code: Sending Control Voltage using Real-time Hand Gesture Recognition

Based on <https://google.github.io/mediapipe/solutions/hands.html>

The distance between index fingers and thumbs of both hands are mapped to a value between 0 and 255 and sent via OSC to pins 25 and 26. When the index finger and thumb are "closed" the Python script sends a trigger to pin 32 and 33.
