#!/usr/bin/env python3
"""
SpatialDrive — Arduino Nano Serial-to-MQTT Wireless Bridge
=========================================================
Reads dual HC-SR04 ultrasonic sensor telemetry from an Arduino Nano over USB Serial (9600 Baud)
and broadcasts live telemetry to the SpatialDrive cloud MQTT room so HUD and Controller
on any device (including iPhone/iPad and Android) receive it instantly with zero lag.

Usage:
    pip install pyserial paho-mqtt
    python serial_bridge.py --room SPATIAL-77
"""

import sys
import time
import re
import json
import argparse

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("\n[!] 'pyserial' is required. Install it using:")
    print("    pip install pyserial\n")
    sys.exit(1)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("\n[!] 'paho-mqtt' is required. Install it using:")
    print("    pip install paho-mqtt\n")
    sys.exit(1)


def find_arduino_port():
    """Auto-detects USB COM port connected to Arduino / CH340 / FTDI."""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "arduino" in desc or "ch340" in desc or "ftdi" in desc or "usb-serial" in desc or "usb serial" in desc:
            return p.device
    # Fallback to the first available COM port
    return ports[0].device


def parse_arduino_line(line):
    """
    Parses the user's Arduino Nano output:
    'Sensor 1: 25 cm   |   Sensor 2: 45 cm'
    'Sensor 1: No Echo   |   Sensor 2: 25 cm'
    """
    line = line.strip()
    if not line:
        return None

    m1 = re.search(r"Sensor\s*1:\s*(-?\d+|No\s*Echo)", line, re.IGNORECASE)
    m2 = re.search(r"Sensor\s*2:\s*(-?\d+|No\s*Echo)", line, re.IGNORECASE)

    if m1 or m2:
        d1 = 999
        d2 = 999
        if m1:
            val1 = m1.group(1).strip()
            d1 = 999 if ("echo" in val1.lower() or int(val1) < 0) else int(val1)
        if m2:
            val2 = m2.group(1).strip()
            d2 = 999 if ("echo" in val2.lower() or int(val2) < 0) else int(val2)
        return d1, d2

    # Fallback for comma-separated or JSON
    if line.startswith("{") and line.endswith("}"):
        try:
            d = json.loads(line)
            d1 = d.get("d1", d.get("distL", 999))
            d2 = d.get("d2", d.get("distR", 999))
            return int(d1), int(d2)
        except Exception:
            pass

    return None


def main():
    parser = argparse.ArgumentParser(description="SpatialDrive Arduino Nano Serial-to-MQTT Bridge")
    parser.add_argument("--port", type=str, default=None, help="Serial COM Port (e.g. COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=9600, help="Serial Baud Rate (default 9600)")
    parser.add_argument("--room", type=str, default="SPATIAL-77", help="Pairing Room Code (default SPATIAL-77)")
    parser.add_argument("--broker", type=str, default="broker.emqx.io", help="MQTT Broker Host")
    args = parser.parse_args()

    port = args.port or find_arduino_port()
    if not port:
        print("[X] No COM ports detected. Please plug in your Arduino Nano via USB.")
        sys.exit(1)

    room_code = args.room.upper().strip()
    topic = f"spatialdrive/{room_code}/telemetry"

    print("=" * 65)
    print("  SPATIALDRIVE ARDUINO NANO WIRELESS BRIDGE")
    print(f"  • Serial Port : {port} @ {args.baud} Baud")
    print(f"  • Room Code   : {room_code}")
    print(f"  • MQTT Topic  : {topic}")
    print(f"  • MQTT Broker : {args.broker}")
    print("=" * 65)

    # Initialize MQTT client
    client = mqtt.Client(client_id=f"py_bridge_{int(time.time())}")
    try:
        client.connect(args.broker, 1883, 60)
        client.loop_start()
        print(f"[✓] Connected to MQTT Broker ({args.broker})")
    except Exception as e:
        print(f"[X] Failed to connect to MQTT broker {args.broker}: {e}")
        print("    Trying fallback broker 'broker.hivemq.com'...")
        try:
            client.connect("broker.hivemq.com", 1883, 60)
            client.loop_start()
            print("[✓] Connected to Fallback Broker (broker.hivemq.com)")
        except Exception as e2:
            print(f"[X] Fallback failed: {e2}")
            sys.exit(1)

    # Open Serial connection
    try:
        ser = serial.Serial(port, args.baud, timeout=1.0)
        time.sleep(1.8)  # Allow Arduino bootloader to initialize
        print(f"[✓] Connected to Arduino Nano on {port}!\n")
    except Exception as e:
        print(f"[X] Failed to open {port}: {e}")
        sys.exit(1)

    print("Streaming live ultrasonic telemetry to HUD & Controller...\n")
    print("   [Press Ctrl+C to terminate]")
    print("-" * 65)

    last_pub_time = 0
    try:
        while True:
            raw = ser.readline().decode("utf-8", errors="ignore")
            parsed = parse_arduino_line(raw)
            if parsed:
                d1, d2 = parsed
                now = time.time()
                # Rate limit transmission to ~30Hz
                if now - last_pub_time >= 0.033:
                    last_pub_time = now
                    payload = {
                        "distL": d1,
                        "distR": d2,
                        "distance": min(d1, d2)
                    }
                    client.publish(topic, json.dumps(payload), qos=0)

                    # Status line
                    s1_warn = " [YELLOW <30cm]" if d1 < 30 else " [NORMAL]"
                    s2_warn = " [YELLOW <30cm]" if d2 < 30 else " [NORMAL]"
                    hazard_str = " *** BOTH YELLOW -> HAZARD ALERT! ***" if (d1 < 30 and d2 < 30) else ""
                    print(f"\r  Left (S1): {d1:3d} cm{s1_warn}  |  Right (S2): {d2:3d} cm{s2_warn}{hazard_str}    ", end="")
                    sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n\n[!] Stopping bridge...")
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()
        print("[✓] Bridge closed cleanly.")


if __name__ == "__main__":
    main()
