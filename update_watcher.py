import os
import ssl
import json
import requests
import shutil
import zipfile
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from datetime import datetime

load_dotenv()

VERSION_FILE = "version.txt"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CLIENT_SCRIPT = os.path.join(BASE_PATH, "client-mqtt.py")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_current_version():
    try:
        with open(os.path.join(BASE_PATH, VERSION_FILE), "r") as f:
            return f.read().strip()
    except:
        return "0.0.0"

def save_version(version):
    with open(os.path.join(BASE_PATH, VERSION_FILE), "w") as f:
        f.write(version)

def is_newer(new, current):
    return tuple(map(int, new.split("."))) > tuple(map(int, current.split(".")))

def download_and_extract_zip(url, extract_to):
    log(f"Descargando actualización desde: {url}")
    response = requests.get(url, stream=True, timeout=10)
    if response.status_code == 200:
        zip_path = os.path.join(BASE_PATH, "update.zip")
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        os.remove(zip_path)
        log("Actualización descargada y descomprimida.")
        return True
    else:
        log(f"Error al descargar: HTTP {response.status_code}")
        return False

def apply_update(version, url):
    temp_dir = os.path.join(BASE_PATH, "update_tmp")
    os.makedirs(temp_dir, exist_ok=True)

    if not download_and_extract_zip(url, temp_dir):
        return

    log("Copying updated files...")

    for root, dirs, files in os.walk(temp_dir):
        rel_path = os.path.relpath(root, temp_dir)
        target_path = os.path.join(BASE_PATH, rel_path)

        os.makedirs(target_path, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_path, file)

            try:
                shutil.copy2(src_file, dst_file)
                log(f"Updated: {os.path.join(rel_path, file)}")
            except Exception as e:
                log(f"⚠️ Failed to copy {file}: {e}")

    shutil.rmtree(temp_dir)
    save_version(version)

    log("Restarting client service...")
    os.system("sudo systemctl restart mqtt-client.service")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        version = payload.get("version")
        global update_url
        update_url = payload.get("url")

        current = get_current_version()
        log(f"Versión actual: {current}, nueva: {version}")

        if is_newer(version, current):
            log("Nueva versión disponible")
            apply_update(version)
        else:
            log("Ya tienes la última versión")

    except Exception as e:
        log(f"Error procesando mensaje: {e}")

def main():
    log("Iniciando watcher de actualizaciones...")

    client = mqtt.Client()
    client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.on_message = on_message

    try:
        client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT", 8883)))
        client.subscribe("device/raspberry123/update")  # <-- Personaliza este topic
        client.loop_forever()
    except Exception as e:
        log(f"Error conectando al broker MQTT: {e}")

if __name__ == "__main__":
    main()