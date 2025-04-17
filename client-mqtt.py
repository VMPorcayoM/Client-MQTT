# client_mqtt_display_auto.py
import paho.mqtt.client as mqtt
import requests
from PIL import Image, ImageTk
import tkinter as tk
import io
import sys

class AutoScreenApp:
    def __init__(self, master):
        self.master = master
        self.setup_display()
        self.setup_mqtt()
        
    def setup_display(self):
        # Configuración agresiva de pantalla completa
        self.master.attributes('-fullscreen', True)
        self.master.overrideredirect(True)  # Elimina bordes y controles
        self.master.configure(bg='black')
        
        # Obtener dimensiones REALES de la pantalla actual
        self.update_screen_dimensions()
        
        # Label principal que ocupará toda la pantalla
        self.label = tk.Label(self.master, bg='black', borderwidth=0)
        self.label.pack(fill=tk.BOTH, expand=True)
        
        # Actualizar dimensiones cuando cambie la pantalla
        self.master.bind('<Configure>', self.on_window_change)
    
    def update_screen_dimensions(self):
        # Actualiza las dimensiones basado en la ventana actual
        self.screen_width = self.master.winfo_width()
        self.screen_height = self.master.winfo_height()
        
        # Si las dimensiones son 1x1 (no inicializadas), usar screeninfo
        if self.screen_width <= 1 or self.screen_height <= 1:
            try:
                from screeninfo import get_monitors
                monitors = get_monitors()
                # Encontrar el monitor que contiene la ventana
                x, y = self.master.winfo_x(), self.master.winfo_y()
                for m in monitors:
                    if m.x <= x <= m.x + m.width and m.y <= y <= m.y + m.height:
                        self.screen_width = m.width
                        self.screen_height = m.height
                        break
                else:  # Si no se encuentra, usar el primer monitor
                    if monitors:
                        self.screen_width = monitors[0].width
                        self.screen_height = monitors[0].height
            except ImportError:
                # Fallback si screeninfo no está disponible
                self.screen_width = self.master.winfo_screenwidth()
                self.screen_height = self.master.winfo_screenheight()
    
    def on_window_change(self, event):
        """Se ejecuta cuando la ventana cambia de pantalla"""
        self.update_screen_dimensions()
    
    def setup_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set("raspberry", "Mawxab-jynqun-1dyzru")
        self.client.connect("u2135bf1.ala.us-east-1.emqxsl.com", 8883)
        self.client.tls_set()
        
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("display/image")
    
    def on_message(self, client, userdata, msg):
        url = msg.payload.decode()
        self.display_image_from_url(url)
    
    def display_image_from_url(self, url):
        try:
            response = requests.get(url, timeout=5)
            content_type = response.headers.get("Content-Type", "")
            print("El tipo de archivo es: "+content_type)
            if "image" not in content_type:
                print(f"⚠️ El contenido no es una imagen. Content-Type: {content_type}")
                return

            # Guarda para inspección si es necesario
            with open("debug_image.jpg", "wb") as f:
                f.write(response.content)

            image_data = io.BytesIO(response.content)
            image_data.seek(0)  # Asegura que el cursor esté al inicio

            try:
                # Intenta abrir y verificar la imagen
                img = Image.open(image_data)
                img.verify()  # Verifica sin cargar completamente
            except Exception as e:
                print("❌ La imagen no pasó verificación:", e)
                return

            # Reabrimos después de verificar
            image_data.seek(0)
            img = Image.open(image_data)

            # Redimensionar y mostrar
            img = img.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)
            self.label.config(image=self.tk_image)
            self.label.update_idletasks()

        except Exception as e:
            print(f"❌ Error al mostrar imagen:", e)

if __name__ == "__main__":
    root = tk.Tk()

    app = AutoScreenApp(root)
    root.mainloop()