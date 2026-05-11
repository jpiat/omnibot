#include "MotorController.h"

MotorController::MotorController(uint8_t pwmPin, uint8_t dirPin, bool reverse)
    : _pwmPin(pwmPin), _dirPin(dirPin), _reverse(reverse) {}

void MotorController::begin() {
    pinMode(_pwmPin, OUTPUT);
    pinMode(_dirPin, OUTPUT);
    analogWrite(_pwmPin, 0);
    digitalWrite(_dirPin, LOW);
}

void MotorController::setSpeed(float speed) {
    speed = constrain(speed, -1.0f, 1.0f);
    if (_reverse) speed = -speed;

    if (speed >= 0.0f) {
        digitalWrite(_dirPin, LOW);
    } else {
        digitalWrite(_dirPin, HIGH);
    }

    uint8_t duty = (uint8_t)(fabs(speed) * 255.0f);
    analogWrite(_pwmPin, duty);
}
