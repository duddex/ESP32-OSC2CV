/*
 * Based on
*   https://www.youtube.com/watch?v=GKnuqrTxj9k&ab_channel=janfiess
*   https://github.com/janfiess/NodeMCU_OSC
*
*  Using the OSC library from <https://github.com/CNMAT/OSC>
*/

#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>

// Replace with your network credentials
const char* ssid = "ESP32-OSC-Access-Point";
const char* password = "123456789";

int x = 0;
int y = 0;
int oldx = 0;
int oldy = 0; 
WiFiUDP Udp;

void setup() {
    Serial.begin(115200);

    // Connect to Wi-Fi network with SSID and password
    Serial.print("Setting AP (Access Point)...");

    // Remove the password parameter, if you want the AP (Access Point) to be open
    WiFi.softAP(ssid, password);

    Serial.print("AP IP address: ");
    Serial.println(WiFi.softAPIP());
  
    // local port to listen for UDP packets
    Udp.begin(8000);

    // There are 2 x 8 bits DAC channels on the ESP32 to convert digital signals into
    // analog voltage signal outputs. These are the DAC channels: DAC1 (GPIO25), DAC2 (GPIO26)
    pinMode(25, ANALOG);
    pinMode(26, ANALOG);

    pinMode(2, OUTPUT);
    pinMode(32, OUTPUT);
    pinMode(33, OUTPUT);
    digitalWrite(2, LOW);
    digitalWrite(32, LOW);
    digitalWrite(33, LOW);
}

// ----------------------------------------------------------------------
void loop() {
  receiveOSC();

  // only update output if x has changed
  if (x != oldx) {
    //Serial.print("x changed: ");
    //Serial.println(x);
    dacWrite(25, x);
    oldx = x;
  }

  // only update output if y has changed
  if (y != oldy) {
    //Serial.print("y changed: ");
    //Serial.println(y);
    dacWrite(26, y);
    oldy = y;
  }
}

// ----------------------------------------------------------------------
void receiveOSC() {
    OSCMessage msgIN;
    int size;
    if ((size = Udp.parsePacket()) > 0) {
        while (size--) {
            msgIN.fill(Udp.read());
        }

        if (!msgIN.hasError()) {
            msgIN.route("/1/push", builtinLED);
            msgIN.route("/2/xy", xyControl);
            msgIN.route("/3/fader1", fader1);
            msgIN.route("/3/fader2", fader2);
            msgIN.route("/3/push1", trigger1);
            msgIN.route("/3/push2", trigger2);
        }
    }
}

// ----------------------------------------------------------------------
void xyControl(OSCMessage &msg, int addrOffset) {
    x = msg.getFloat(0);
    y = msg.getFloat(1);
}

// ----------------------------------------------------------------------
void fader1(OSCMessage &msg, int addrOffset) {
    x = msg.getFloat(0);
}

// ----------------------------------------------------------------------
void fader2(OSCMessage &msg, int addrOffset) {
    y = msg.getFloat(0);
}

// ----------------------------------------------------------------------
void builtinLED(OSCMessage &msg, int addrOffset) {
    if (msg.getFloat(0) == 0) {
      digitalWrite(2, LOW); // 2 = Builtin LED on ESP32
    } else {
      digitalWrite(2, HIGH);
    }
}

// ----------------------------------------------------------------------
void trigger1(OSCMessage &msg, int addrOffset) {
    if (msg.getFloat(0) == 0) {
      digitalWrite(32, LOW);
    } else {
      digitalWrite(32, HIGH);
    }
}

// ----------------------------------------------------------------------
void trigger2(OSCMessage &msg, int addrOffset) {
    if (msg.getFloat(0) == 0) {
      digitalWrite(33, LOW);
    } else {
      digitalWrite(33, HIGH);
    }
}
