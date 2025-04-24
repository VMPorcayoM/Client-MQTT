📡 Raspberry Pi MQTT Image Display – Remote Updater
===================================================

This project enables your Raspberry Pi to display full-screen images via MQTT 
and update its display script remotely over a cellular connection with minimal 
data usage. Ideal for remotely managed screens in IoT environments.

---------------------------------------------------
📁 Project Structure
---------------------------------------------------

/home/pi/scripts/
├── main/                      # Main script directory (auto-updated)
│   ├── client-mqtt.py         # Main image display script
│   ├── .env                   # MQTT/Azure configuration
│   ├── version.txt            # Current version number
│   └── other files...
├── update_watcher.py          # MQTT-based update watcher
├── update_watcher.service     # systemd unit for the watcher
├── venv/                      # Python virtual environment

---------------------------------------------------
⚙️ How the Remote Update Works
---------------------------------------------------

1. A ZIP file with updated files is uploaded to your server (e.g. Azure Blob).
2. A JSON MQTT message is published to a topic like:
     device/raspberry123/update
   With payload:
     {
       "version": "1.0.3",
       "url": "https://your-server.com/client-v1.0.3.zip"
     }

3. update_watcher.py listens for this message.
4. If the version is newer:
   - It downloads and extracts the ZIP
   - Copies files to /home/pi/scripts/main/
   - Updates version.txt
   - Restarts the display service

✅ Efficient, ✅ Safe, ✅ No SSH needed, ✅ Low data usage

---------------------------------------------------
🧰 Installation Steps
---------------------------------------------------

1. Create project structure:

   mkdir -p /home/pi/scripts/main
   cd /home/pi/scripts

2. Copy or clone your client-mqtt.py and others into `main/`

3. Create Python virtual environment:

   python3 -m venv venv
   source venv/bin/activate

4. Install dependencies:

   sudo apt install -y libjpeg-dev zlib1g-dev libfreetype6-dev \
   liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk python3-dev

   pip install paho-mqtt python-dotenv Pillow requests screeninfo

---------------------------------------------------
📄 .env File (in /home/pi/scripts/main/)
---------------------------------------------------

MQTT_BROKER=your-mqtt-broker.com
MQTT_PORT=8883
MQTT_USERNAME=youruser
MQTT_PASSWORD=yourpassword
MQTT_TOPIC=display/image
AZURE_URL_BASE=https://yourblob.blob.core.windows.net/images/

---------------------------------------------------
🔁 Setting Up the Update Watcher
---------------------------------------------------

1. Place update_watcher.py in /home/pi/scripts/

2. Create systemd service:

   sudo nano /etc/systemd/system/update-watcher.service

   [Unit]
   Description=Update watcher for MQTT image display
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/scripts
   ExecStart=/home/pi/scripts/venv/bin/python /home/pi/scripts/update_watcher.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target

3. Enable and start the service:

   sudo systemctl daemon-reload
   sudo systemctl enable update-watcher.service
   sudo systemctl start update-watcher.service

---------------------------------------------------
🧪 Example Update Flow
---------------------------------------------------

1. Create ZIP from /main/:

   cd /home/pi/scripts/main
   zip -r ../client-v1.0.3.zip .

2. Upload to server or Azure Blob

3. Send MQTT message to topic device/raspberry123/update:

   {
     "version": "1.0.3",
     "url": "https://yourserver.com/client-v1.0.3.zip"
   }

---------------------------------------------------
✅ Best Practices
---------------------------------------------------

- Do not include venv/ or update_watcher.py in the ZIP
- Use versioning: 1.0.1, 1.0.2, etc.
- Test ZIPs on staging before production
- Use screeninfo in your client to adapt resolution

---------------------------------------------------
📞 Support
---------------------------------------------------

Feel free to expand the updater for grouped devices or secure brokers.