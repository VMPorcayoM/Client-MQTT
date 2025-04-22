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