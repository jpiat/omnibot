#include "OmniMixer.h"
#include <math.h>

OmniMixer::OmniMixer(MotorController& frontLeft, MotorController& frontRight,
                     MotorController& rearLeft, MotorController& rearRight)
    : _fl(frontLeft), _fr(frontRight), _rl(rearLeft), _rr(rearRight) {}

void OmniMixer::begin() {
    _fl.begin();
    _fr.begin();
    _rl.begin();
    _rr.begin();
}

void OmniMixer::drive(float x, float y, float rotation) {
    x = constrain(x, -1.0f, 1.0f);
    y = constrain(y, -1.0f, 1.0f);
    rotation = constrain(rotation, -1.0f, 1.0f);

    // Mecanum/omni kinematic mixing
    float fl =  x + y + rotation;
    float fr = -x + y - rotation;
    float rl = -x + y + rotation;
    float rr =  x + y - rotation;

    // Normalize so no motor exceeds ±1
    float maxMag = fmax(fmax(fabs(fl), fabs(fr)), fmax(fabs(rl), fabs(rr)));
    if (maxMag > 1.0f) {
        fl /= maxMag;
        fr /= maxMag;
        rl /= maxMag;
        rr /= maxMag;
    }

    _fl.setSpeed(fl);
    _fr.setSpeed(fr);
    _rl.setSpeed(rl);
    _rr.setSpeed(rr);
}

void OmniMixer::stop() {
    _fl.setSpeed(0.0f);
    _fr.setSpeed(0.0f);
    _rl.setSpeed(0.0f);
    _rr.setSpeed(0.0f);
}
