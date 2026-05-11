#pragma once

#include <Arduino.h>
#include <WebSocketsServer.h>
#include "OmniMixer.h"

// Binary command packet: 3 x float32 little-endian = 12 bytes
// [0..3] x  (strafe)
// [4..7] y  (forward)
// [8..11] rotation

class RobotServer {
public:
    RobotServer(OmniMixer& mixer, uint16_t port = 81);
    void begin(const char* ssid, const char* password);
    void loop();

private:
    static constexpr unsigned long WATCHDOG_TIMEOUT_MS = 500;
    static constexpr size_t CMD_PACKET_SIZE = 12; // 3 floats

    void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length);

    OmniMixer& _mixer;
    WebSocketsServer _ws;
    unsigned long _lastCmdTime;
    bool _active;
};
