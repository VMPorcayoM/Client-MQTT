# Raspberry Pi MQTT Image Display Setup

This guide explains how to set up and run the `client-mqtt.py` script on a Raspberry Pi with a graphical environment.

## 📦 Requirements

- Raspberry Pi OS with GUI
- Python 3 (already included in Raspberry Pi OS)
- Internet connection
- A connected display

## 🧰 Step-by-step Setup

### 1. Clone or Copy the Project

Copy the project directory to your Raspberry Pi, or clone it from a repository if applicable.

### 2. Create a Python Virtual Environment

Open a terminal and run:

```bash
python3 -m venv venv
source venv/bin/activate

### 3. Install Python Dependencies
Base system necessary to compile Pillow:

sudo apt update
sudo apt install -y \
libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev \
tcl8.6-dev tk8.6-dev python3-tk python3-dev python3-venv

Make sure you’re in the same folder as the requirements.txt file and run:

pip install -r requirements.txt

### 4. Create the .env File

In the root of the project directory, create a file named .env and add the following:
MQTT_BROKER=your-mqtt-broker-url
MQTT_PORT=8883
MQTT_USERNAME=your-username
MQTT_PASSWORD=your-password
MQTT_TOPIC=display/image

AZURE_URL_BASE=https://your-blob-storage-url/

Replace values with your actual MQTT broker credentials and base URL for image validation.

### 5. Run the Script

While the virtual environment is active, run the script using:
python client-mqtt.py

🔄 Set Up Automatic Execution on Boot (systemd)

### 6. Create a systemd service
Create the following file:
sudo nano /etc/systemd/system/mqtt-client.service

Paste the following content:
[Unit]
Description=MQTT Image Display Client
After=network.target graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/scripts
ExecStart=/home/pi/scripts/venv/bin/python /home/pi/scripts/client-mqtt.py
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target


Replace paths with your actual script location if different.

### 7. Enable and Start the Service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable mqtt-client.service
sudo systemctl start mqtt-client.service

### 8. Check Service Status and Logs
systemctl status mqtt-client.service

To view logs in real time:
journalctl -fu mqtt-client.service