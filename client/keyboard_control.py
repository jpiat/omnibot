#!/usr/bin/env python3
"""Keyboard + DualShock 4 WebSocket client for the omnibot.

Keyboard:
    W / S  — forward / backward
    A / D  — strafe left / right
    Q / E  — rotate left / right
    ESC    — quit

DualShock 4 (PS4):
    Left stick  — X/Y translation
    Right stick X — Z rotation

Sends 12-byte binary packets (3 x float32 LE): [x, y, rotation]
at ~20 Hz. Gamepad input takes priority when sticks are moved.
"""

import argparse
import struct
import sys
import threading
import time

import websocket

try:
    import curses
except ImportError:
    print("curses is required (standard on Linux/macOS, install windows-curses on Windows)")
    sys.exit(1)

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

SEND_RATE = 0.05  # 20 Hz
DEADZONE = 0.1


def apply_deadzone(value: float, deadzone: float = DEADZONE) -> float:
    if abs(value) < deadzone:
        return 0.0
    return value


def main(stdscr, uri: str, speed: float, use_joystick: bool):
    stdscr.nodelay(True)
    stdscr.clear()
    stdscr.addstr(0, 0, f"Connected to {uri}")
    stdscr.addstr(1, 0, "W/S=fwd/back  A/D=strafe  Q/E=rotate  ESC=quit")
    stdscr.addstr(2, 0, f"Speed: {speed:.1f}")

    joystick = None
    if use_joystick and HAS_PYGAME:
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            stdscr.addstr(3, 0, f"Gamepad: {joystick.get_name()}")
        else:
            stdscr.addstr(3, 0, "No gamepad found, using keyboard only")
    elif use_joystick and not HAS_PYGAME:
        stdscr.addstr(3, 0, "pygame not installed, using keyboard only")

    ws = websocket.WebSocket()
    ws.connect(uri)

    keys_held = set()
    joy_x = 0.0
    joy_y = 0.0
    joy_rot = 0.0
    joy_lock = threading.Lock()
    running = True

    def joystick_reader():
        nonlocal joy_x, joy_y, joy_rot
        while running:
            if joystick is None:
                time.sleep(0.1)
                continue
            pygame.event.pump()
            # Left stick: axis 0 = X (strafe), axis 1 = Y (forward, inverted)
            # Right stick: axis 3 = X (rotation)
            lx = apply_deadzone(joystick.get_axis(0))
            ly = apply_deadzone(-joystick.get_axis(1))  # invert Y
            rx = apply_deadzone(joystick.get_axis(3))
            with joy_lock:
                joy_x = lx
                joy_y = ly
                joy_rot = rx
            time.sleep(SEND_RATE)

    def sender():
        while running:
            # Keyboard contribution
            kx = 0.0
            ky = 0.0
            krot = 0.0

            if ord('a') in keys_held:
                kx -= speed
            if ord('d') in keys_held:
                kx += speed
            if ord('w') in keys_held:
                ky += speed
            if ord('s') in keys_held:
                ky -= speed
            if ord('q') in keys_held:
                krot -= speed
            if ord('e') in keys_held:
                krot += speed

            # Gamepad contribution (scaled by speed)
            with joy_lock:
                gx = joy_x * speed
                gy = joy_y * speed
                grot = joy_rot * speed

            # Combine: use gamepad if active, otherwise keyboard
            if abs(gx) > 0 or abs(gy) > 0 or abs(grot) > 0:
                x, y, rot = gx, gy, grot
            else:
                x, y, rot = kx, ky, krot

            x = max(-1.0, min(1.0, x))
            y = max(-1.0, min(1.0, y))
            rot = max(-1.0, min(1.0, rot))

            packet = struct.pack('<fff', x, y, rot)
            try:
                ws.send_binary(packet)
            except Exception:
                break

            src = "gamepad" if (abs(gx) > 0 or abs(gy) > 0 or abs(grot) > 0) else "keyboard"
            stdscr.addstr(5, 0, f"[{src:8s}] x={x:+.2f}  y={y:+.2f}  rot={rot:+.2f}   ")
            stdscr.refresh()
            time.sleep(SEND_RATE)

    if joystick is not None:
        tj = threading.Thread(target=joystick_reader, daemon=True)
        tj.start()

    t = threading.Thread(target=sender, daemon=True)
    t.start()

    try:
        while True:
            ch = stdscr.getch()
            if ch == -1:
                time.sleep(0.01)
                continue
            if ch == 27:  # ESC
                break
            if ch == curses.KEY_UP or ch == ord('w'):
                keys_held.add(ord('w'))
            elif ch == curses.KEY_DOWN or ch == ord('s'):
                keys_held.add(ord('s'))
            elif ch == curses.KEY_LEFT or ch == ord('a'):
                keys_held.add(ord('a'))
            elif ch == curses.KEY_RIGHT or ch == ord('d'):
                keys_held.add(ord('d'))
            elif ch == ord('q'):
                keys_held.add(ord('q'))
            elif ch == ord('e'):
                keys_held.add(ord('e'))

            def clear_key(k):
                time.sleep(0.15)
                keys_held.discard(k)

            if ch != -1 and ch != 27:
                threading.Thread(target=clear_key, args=(ch,), daemon=True).start()
    finally:
        running = False
        try:
            ws.send_binary(struct.pack('<fff', 0.0, 0.0, 0.0))
        except Exception:
            pass
        ws.close()
        if joystick is not None:
            pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omnibot keyboard/gamepad controller")
    parser.add_argument("--host", default="10.157.207.107", help="Pico W IP address")
    parser.add_argument("--port", type=int, default=81, help="WebSocket port")
    parser.add_argument("--speed", type=float, default=0.55, help="Speed factor 0.0-1.0")
    parser.add_argument("--no-joystick", action="store_true", help="Disable gamepad input")
    args = parser.parse_args()

    uri = f"ws://{args.host}:{args.port}"
    curses.wrapper(lambda stdscr: main(stdscr, uri, args.speed, not args.no_joystick))
