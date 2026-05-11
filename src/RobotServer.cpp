#include "RobotServer.h"
#include <WiFi.h>

RobotServer::RobotServer(OmniMixer& mixer, uint16_t port)
    : _mixer(mixer), _ws(port), _lastCmdTime(0), _active(false) {}

void RobotServer::begin(const char* ssid, const char* password) {
    WiFi.begin(ssid, password);
    //Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        //Serial.print(".");
    }
    //Serial.println();
    //Serial.print("IP: ");
    //Serial.println(WiFi.localIP());

    _ws.begin();
    _ws.onEvent([this](uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
        this->onWebSocketEvent(num, type, payload, length);
    });

    //Serial.println("WebSocket server started");
}

void RobotServer::loop() {
    _ws.loop();

    // Watchdog: stop if no command received within timeout
    if (_active && (millis() - _lastCmdTime > WATCHDOG_TIMEOUT_MS)) {
        _mixer.stop();
        _active = false;
        //Serial.println("Watchdog: no command received, stopping");
    }
}

void RobotServer::onWebSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
    switch (type) {
        case WStype_CONNECTED:
            //Serial.printf("Client [%u] connected\n", num);
            break;

        case WStype_DISCONNECTED:
            //Serial.printf("Client [%u] disconnected\n", num);
            _mixer.stop();
            _active = false;
            break;

        case WStype_BIN:
            if (length == CMD_PACKET_SIZE) {
                float x, y, rotation;
                memcpy(&x, payload, sizeof(float));
                memcpy(&y, payload + sizeof(float), sizeof(float));
                memcpy(&rotation, payload + 2 * sizeof(float), sizeof(float));

                _mixer.drive(x, y, rotation);
                _lastCmdTime = millis();
                _active = true;
            }
            break;

        default:
            break;
    }
}
