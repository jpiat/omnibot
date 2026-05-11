#pragma once

#include <Arduino.h>

class MotorController {
public:
    MotorController(uint8_t pwmPin, uint8_t dirPin, bool reverse = false);
    void begin();
    void setSpeed(float speed);

private:
    uint8_t _pwmPin;
    uint8_t _dirPin;
    bool _reverse;
};
