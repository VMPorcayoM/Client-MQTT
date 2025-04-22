import os
import io
import ssl
import requests
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Load environment variables
load_dotenv()

class AutoScreenApp:
    def __init__(self, master):
        self.master = master
        self.setup_display()
        self.setup_mqtt()
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def setup_display(self):
        self.master.attributes('-fullscreen', True)
        self.master.overrideredirect(True)
        self.master.configure(bg='black')
        self.update_screen_dimensions()

        self.label = tk.Label(self.master, bg='black', borderwidth=0)
        self.label.pack(fill=tk.BOTH, expand=True)
        self.master.bind('<Configure>', self.on_window_change)

    def update_screen_dimensions(self):
        self.screen_width = self.master.winfo_width()
        self.screen_height = self.master.winfo_height()
        if self.screen_width <= 1 or self.screen_height <= 1:
            try:
                from screeninfo import get_monitors
                monitors = get_monitors()
                if monitors:
                    self.screen_width = monitors[0].width
                    self.screen_height = monitors[0].height
            except:
                self.screen_width = self.master.winfo_screenwidth()
                self.screen_height = self.master.winfo_screenheight()

    def on_window_change(self, event):
        self.update_screen_dimensions()

    def setup_mqtt(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(
            os.getenv("MQTT_USERNAME"),
            os.getenv("MQTT_PASSWORD")
        )
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(
                os.getenv("MQTT_BROKER"),
                int(os.getenv("MQTT_PORT", 8883))
            )
            self.client.loop_start()
            self.log("🔐 Conectado a MQTT seguro")
        except Exception as e:
            self.log(f"Error al conectar a MQTT: {e}")

    def on_connect(self, client, userdata, flags, rc):
        topic = os.getenv("MQTT_TOPIC", "display/image")
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        url = msg.payload.decode()
        self.log(f"URL recibida: {url}")
        self.display_image_from_url(url)

    def display_image_from_url(self, url):
        # Seguridad: validar origen de la URL
        base = os.getenv("AZURE_URL_BASE", "")
        if not url.startswith(base):
            self.log("URL no permitida")
            return

        for attempt in range(3):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    break
            except Exception as e:
                self.log(f"Intento {attempt+1} falló: {e}")
        else:
            self.log("Falló la descarga tras 3 intentos")
            self.display_placeholder()
            return

        try:
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                self.log(f"No es imagen válida. Tipo: {content_type}")
                self.display_placeholder()
                return

            image_data = io.BytesIO(response.content)
            image_data.seek(0)  # Asegura que el cursor esté al inicio

            try:
                # Intenta abrir y verificar la imagen
                img = Image.open(image_data)
                img.verify()  # Verifica sin cargar completamente
            except Exception as e:
                self.log(f"Verificación de imagen fallida: {e}")
                self.display_placeholder()
                return

            image_data.seek(0)
            img = Image.open(image_data)
            img = img.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)
            self.label.config(image=self.tk_image)
            self.label.update_idletasks()

        except Exception as e:
            self.log(f"Error al mostrar imagen: {e}")
            self.display_placeholder()

    def display_placeholder(self):
        # Mostrar pantalla negra en caso de error
        self.label.config(image='', bg='black')
        self.label.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()

    app = AutoScreenApp(root)
    root.mainloop()