#!/usr/bin/env python3
"""Debug script to display all joystick axes, buttons, and hats in real-time."""

import pygame
import sys
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick found.")
    sys.exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Name: {joystick.get_name()}")
print(f"Axes: {joystick.get_numaxes()}")
print(f"Buttons: {joystick.get_numbuttons()}")
print(f"Hats: {joystick.get_numhats()}")
print("-" * 60)

try:
    while True:
        pygame.event.pump()

        axes = [f"{joystick.get_axis(i):+.3f}" for i in range(joystick.get_numaxes())]
        buttons = [str(joystick.get_button(i)) for i in range(joystick.get_numbuttons())]
        hats = [str(joystick.get_hat(i)) for i in range(joystick.get_numhats())]

        print(f"\rAxes: [{', '.join(axes)}]  Buttons: [{','.join(buttons)}]  Hats: {hats}", end="")
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nDone.")
    pygame.quit()
