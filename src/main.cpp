#include <Arduino.h>
#include "OmniMixer.h"
#include "RobotServer.h"
#include "wifi_config.h"

// Motor pins: (PWM, DIR)
// Front-Left, Front-Right, Rear-Left, Rear-Right
MotorController motorFL(10, 11);
MotorController motorFR(14, 15, true);
MotorController motorRL(17, 16);
MotorController motorRR(21, 20, true);

OmniMixer mixer(motorFL, motorFR, motorRL, motorRR);
RobotServer server(mixer);

void setup() {
    //Serial.begin(115200);
    mixer.begin();
    server.begin(WIFI_SSID, WIFI_PASS);
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {
    server.loop();

}