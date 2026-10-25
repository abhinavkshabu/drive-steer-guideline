# SpatialDrive — Dual-Screen AR HUD & Wireless Controller Hub

SpatialDrive is a high-performance, cross-device IoT telematics system that runs in mobile and desktop web browsers. It splits the driving cockpit experience across two devices:
- **Mobile 1 (Controller):** Interactive steering wheel with touch & gyro tilt steering, paddle shifters, detent clicks, and obstacle proximity simulation.
- **Mobile 2 (HUD Display):** Real-time Augmented Reality Head-Up Display with dynamic Ackermann trajectory guidelines, horizon reticle, windshield reflection mirror mode, and collision alerts.

Both devices sync in real-time over any **Wi-Fi, 4G, or 5G network** using secure MQTT WebSockets (`wss://broker.emqx.io:8084/mqtt`).

---

## 🚀 How to Deploy Online (GitHub Pages in 3 Clicks)

Since your project is on GitHub, follow these steps to deploy it live with a free, secure `https://` link:

1. **Push the updated files** (`index.html`, `controller.html`, `hud.html`) to your GitHub repository.
2. On GitHub, navigate to your repository and click **Settings** (top navigation tab).
3. In the left sidebar, click **Pages** (under the *Code and automation* section).
4. Under **Build and deployment > Source**, select:
   - **Branch:** `main` (or `master`)
   - **Folder:** `/ (root)`
5. Click **Save**.
6. Wait 30–60 seconds. Refresh the page to see your live URL:
   ```
   https://<your-username>.github.io/<your-repo-name>/
   ```

---

## 📱 How to Open on Two Mobiles

1. Open your live GitHub Pages URL on your laptop or on Phone 1:
   ```
   https://<your-username>.github.io/<your-repo-name>/
   ```
2. You will see the **SpatialDrive Hub** (`index.html`) with two QR codes:
   - **Mobile 1:** Scan the **Steering Wheel** QR code (or open `controller.html?room=...`).
   - **Mobile 2:** Scan the **AR HUD** QR code (or open `hud.html?room=...`).
3. Place **Mobile 2** on your desk or car dashboard (tap `HUD MIRROR` if projecting onto a glass windshield).
4. Hold **Mobile 1** in your hands. Turn the wheel or tilt the phone—watch the trajectory curves bend in real time on Mobile 2!

---

## ⚡ Pairing Room Codes

Both pages use a shared **Room Code** (e.g. `SPATIAL-77` or any custom code like `DRIVE-42`):
- `https://<url>/controller.html?room=MY-ROOM`
- `https://<url>/hud.html?room=MY-ROOM`

As long as both phones have the same room code, they will sync privately and instantaneously. You can generate or change room codes directly from `index.html` or by tapping the room indicator in either app.

---

## 🔌 Arduino Nano + Dual HC-SR04 Ultrasonic Sensors

Your setup:
- **Arduino Nano**
- **Sensor 1 (Left):** `TRIG = D2`, `ECHO = D3`
- **Sensor 2 (Right):** `TRIG = D4`, `ECHO = D5`
- **Baud Rate:** `9600` (`Serial.begin(9600)`)
- **Output Format:** `"Sensor 1: <val> cm   |   Sensor 2: <val> cm"`

### 🚦 Visual Feedback Logic:
- **Left Sensor `< 30 cm`:** **Left line turns bright YELLOW** (Right line stays normal cyan).
- **Right Sensor `< 30 cm`:** **Right line turns bright YELLOW** (Left line stays normal cyan).
- **Both Sensors `< 30 cm`:** **Both lines turn YELLOW**, AND the full **Critical Proximity Hazard Warning** triggers (banner + screen edge pulse)!
- **No hazard warning until both turn yellow**: When only one sensor detects an obstacle, only that side's guideline turns yellow without triggering alarms.

---

## 📍 Where & How to Connect the Arduino Nano

You have 3 easy ways to connect:

### 1. Direct to Computer / Laptop running the HUD (Recommended)
1. Plug the Arduino Nano into any USB port on your laptop or PC running [hud.html](file:///c:/Users/Adithyan/OneDrive/Desktop/dsg/hud.html) in Chrome or Edge.
2. Click the top-bar button: **`SERIAL (9600)`**.
3. Choose your Arduino Nano COM port in the browser popup and click **Connect**.
4. That's it! Live distances appear on the HUD telemetry and dynamically color the guidelines.

### 2. Direct to Android Mobile Phone via USB-OTG
1. Plug the Nano into the phone's charging port using a simple USB-C OTG (or Micro-USB OTG) adapter.
2. In Chrome, tap **`SERIAL (9600)`** in either [hud.html](file:///c:/Users/Adithyan/OneDrive/Desktop/dsg/hud.html) or [controller.html](file:///c:/Users/Adithyan/OneDrive/Desktop/dsg/controller.html) and grant USB permission.

### 3. Connect to PC and Stream Wirelessly via Python Bridge (`serial_bridge.py`)
If your HUD or Controller is running on an **iPhone/iPad** (which doesn't support Web Serial API):
1. Plug the Nano into your PC/Laptop USB port.
2. Run the included bridge script:
   ```bash
   pip install pyserial paho-mqtt
   python serial_bridge.py --room SPATIAL-77
   ```
3. The bridge reads the Nano at 9600 baud and streams the dual sensor readings wirelessly over MQTT directly to both phones!
