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
        self.master.configure(bg='black')
        self.master.attributes('-fullscreen', True)
        self.configure_window()
        self.update_screen_dimensions()

        self.label = tk.Label(self.master, bg='black', borderwidth=0)
        self.label.pack(fill=tk.BOTH, expand=True)

    def configure_window(self):
        self.master.configure(bg='black', cursor='none')
        self.master.bind('<Configure>', self.on_window_change)
        self.master.bind('<q>', lambda e: self.quit())
        self.master.bind('<Escape>', lambda e: self.quit())

    def quit(self):
        self.log("👋 Exiting...")
        self.client.loop_stop()
        self.client.disconnect()
        self.master.destroy()

    def update_screen_dimensions(self):
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        if self.screen_width <= 1 or self.screen_height <= 1:
            try:
                from screeninfo import get_monitors
                if monitors := get_monitors():
                    self.screen_width = monitors[0].width
                    self.screen_height = monitors[0].height
            except Exception:
                pass

    def on_window_change(self, event):
        self.update_screen_dimensions()

    def setup_mqtt(self):
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        broker = os.getenv("MQTT_BROKER")
        port = int(os.getenv("MQTT_PORT", 8883))

        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(broker, port)
            self.client.loop_start()
            self.log("Connected to secure MQTT")
        except Exception as e:
            self.log(f"Error connecting to MQTT: {e}")

    def on_connect(self, client, userdata, flags, rc):
        topic = os.getenv("MQTT_TOPIC", "display/image")
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        url = msg.payload.decode()
        self.log(f"Received URL: {url}")
        self.display_image_from_url(url)

    def is_valid_image(self, response):
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            self.log(f"Invalid image type: {content_type}")
            return False

        try:
            image_data = io.BytesIO(response.content)
            img = Image.open(image_data)
            img.verify()
            return True
        except Exception as e:
            self.log(f"Image verification failed: {e}")
            return False

    def display_image_from_url(self, url):
        base = os.getenv("AZURE_URL_BASE", "")
        if not url.startswith(base):
            self.log("URL not allowed")
            return

        for attempt in range(3):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    break
            except Exception as e:
                self.log(f"Attempt {attempt + 1} failed: {e}")
        else:
            self.log("Download failed after 3 attempts")
            self.display_placeholder()
            return

        if not self.is_valid_image(response):
            self.display_placeholder()
            return

        try:
            image_data = io.BytesIO(response.content)
            image_data.seek(0)
            img = Image.open(image_data)
            img = img.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)
            self.label.config(image=self.tk_image)
            self.label.update_idletasks()

        except Exception as e:
            self.log(f"Error displaying image: {e}")
            self.display_placeholder()

    def display_placeholder(self):
        self.label.config(image='', bg='black')
        self.label.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()

    app = AutoScreenApp(root)
    root.mainloop()