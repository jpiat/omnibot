#pragma once

#include "MotorController.h"

class OmniMixer {
public:
    OmniMixer(MotorController& frontLeft, MotorController& frontRight,
              MotorController& rearLeft, MotorController& rearRight);
    void begin();
    void drive(float x, float y, float rotation);
    void stop();

private:
    MotorController& _fl;
    MotorController& _fr;
    MotorController& _rl;
    MotorController& _rr;
};
