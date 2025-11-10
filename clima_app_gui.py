# c:\Users\Oscar Montufar\Documents\GitHub\Clima-Salamandra\clima_app_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime

import math
import os
import sys
# --- CONFIGURACIÓN INICIAL ---
# Usaremos un archivo config.py para la API Key, es una buena práctica.
try:
    from config import API_KEY
except ImportError:
    # Si config.py no existe, creamos una variable vacía.
    # La app pedirá la clave si no la encuentra.
    API_KEY = "7c48b9eb0613e79b86fff1f5e08f59b3"

# --- RUTAS DE ARCHIVOS ---
# Determinar la ruta base para guardar archivos, tanto en modo script como en modo .exe
if getattr(sys, 'frozen', False):
    # Si se ejecuta como un paquete (ej. PyInstaller), la ruta base es el directorio del .exe
    basedir = os.path.dirname(sys.executable)
else:
    # Si se ejecuta como un script .py normal, la ruta base es el directorio del script
    basedir = os.path.dirname(os.path.abspath(__file__))
    
# Ya no necesitamos una plantilla, solo el archivo de salida.
SALIDA_HTML = os.path.join(basedir, 'currenweather.html')

# --- LÓGICA PRINCIPAL (Adaptada del script original) ---

def calculate_dew_point(temp, humidity_percent, units):
    """
    Calcula el punto de rocío (Dew Point) usando la fórmula de Magnus.
    La temperatura debe estar en Celsius para la fórmula.
    """
    # Parámetros de la fórmula de Magnus
    a = 17.27
    b = 237.7

    # Si las unidades son imperiales (Fahrenheit), convertir temp a Celsius para el cálculo
    temp_c = (temp - 32) * 5/9 if units == 'imperial' else temp

    # Calcular el punto de rocío en Celsius
    gamma = (a * temp_c) / (b + temp_c) + math.log(humidity_percent / 100.0)
    dew_point_c = (b * gamma) / (a - gamma)

    # Si las unidades originales eran imperiales, convertir el resultado de nuevo a Fahrenheit
    if units == 'imperial':
        return (dew_point_c * 9/5) + 32
    return dew_point_c

def obtener_y_actualizar_clima(mostrar_exito=True):
    """Función principal que se ejecuta al presionar el botón."""
    
    ciudad = city_entry.get()
    unidades = units_var.get()
    idioma = 'es' # Puedes cambiarlo a 'en' si prefieres inglés

    if not ciudad:
        messagebox.showerror("Error", "Por favor, introduce el nombre de una ciudad.")
        return

    if not API_KEY:
        messagebox.showerror("Error de Configuración", 
                             "No se encontró la API Key. Asegúrate de tener un archivo 'config.py' con tu 'API_KEY' definida.")
        return

    # Mapeo de unidades para la API y para la visualización
    unit_symbol = "°C" if unidades == "metric" else "°F"
    wind_speed_unit = "m/s" if unidades == "metric" else "mph"
    
    # Construir la URL de la API
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units={unidades}&lang={idioma}"

    try:
        # --- 1. Obtener datos de la API ---
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para respuestas no exitosas (4xx, 5xx)
        datos_clima = response.json()

        # --- 2. Extraer y formatear datos ---
        condicion = datos_clima['weather'][0]['description'].capitalize()
        temp = datos_clima['main']['temp']
        sensacion = datos_clima['main']['feels_like']
        humedad = datos_clima['main']['humidity']
        viento = datos_clima['wind']['speed']
        presion = datos_clima['main']['pressure']
        amanecer = datetime.fromtimestamp(datos_clima['sys']['sunrise']).strftime('%I:%M %p')
        atardecer = datetime.fromtimestamp(datos_clima['sys']['sunset']).strftime('%I:%M %p')

        # --- 3. Realizar conversiones para el formato de salida ---

        # Temperaturas: obtener siempre Celsius y Fahrenheit
        temp_c = (temp - 32) * 5/9 if unidades == 'imperial' else temp
        temp_f = temp_c * 9/5 + 32
        feels_c = (sensacion - 32) * 5/9 if unidades == 'imperial' else sensacion
        feels_f = feels_c * 9/5 + 32

        # Punto de rocío: obtener siempre Celsius y Fahrenheit
        dew_point_c = calculate_dew_point(temp, humedad, 'metric')
        dew_point_f = calculate_dew_point(temp, humedad, 'imperial')

        # Viento: convertir m/s a km/h
        viento_ms = viento if unidades == 'metric' else viento * 0.44704
        viento_kmh = viento_ms * 3.6

        # Barómetro: convertir hPa a mmHg
        presion_mmhg = presion * 0.750062

        # --- 4. Construir el contenido del archivo con el nuevo formato ---
        contenido_final = f"""<HTML>
<BR />
Condition: {condicion}<BR />
Temperature:{temp_c:.0f}°C/{temp_f:.0f}°F<BR />
Feels Like: {feels_c:.0f}°C/{feels_f:.0f}°F<BR />
Dew Point: {dew_point_c:.0f}°C/{dew_point_f:.0f}°F<BR />
Humidity: {humedad}%<BR />
Wind: {viento_kmh:.2f} km/h<BR />
Barometer: {presion_mmhg:.0f} mm<BR />
Sunrise: {amanecer}<BR />
Sunset: {atardecer}<BR />
<BR />
</HTML>
"""

        # --- 5. Escribir el nuevo archivo HTML ---
        with open(SALIDA_HTML, 'w', encoding='utf-8') as f:
            f.write(contenido_final)
        
        if mostrar_exito:
            messagebox.showinfo("Éxito", f"El archivo '{SALIDA_HTML}' ha sido generado correctamente.")
        else:
            print(f"Actualización automática a las {datetime.now().strftime('%H:%M:%S')}: Archivo '{SALIDA_HTML}' generado.")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            messagebox.showerror("Error", f"No se pudo encontrar la ciudad: '{ciudad}'.\nPor favor, verifica el nombre.")
        elif e.response.status_code == 401:
            messagebox.showerror("Error", "API Key inválida o no autorizada. Revisa tu archivo 'config.py'.")
        else:
            messagebox.showerror("Error de API", f"Hubo un problema al contactar la API: {e}")
    except FileNotFoundError:
        messagebox.showerror("Error de Archivo", f"No se pudo escribir el archivo en la ruta: '{SALIDA_HTML}'.\nVerifica los permisos de la carpeta.")
    except Exception as e:
        messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")

# --- FUNCIONES PARA LA ACTUALIZACIÓN AUTOMÁTICA ---

auto_update_job_id = None

def auto_update_loop():
    """Realiza la actualización y se reprograma a sí misma."""
    global auto_update_job_id
    obtener_y_actualizar_clima(mostrar_exito=False)
    # Reprograma esta misma función para que se ejecute en 15 minutos (900,000 ms)
    auto_update_job_id = root.after(900000, auto_update_loop)

def toggle_auto_update():
    """Inicia o detiene el ciclo de actualización automática."""
    global auto_update_job_id
    if auto_update_var.get():
        print("Iniciando actualización automática cada 15 minutos.")
        # Inicia el bucle
        auto_update_loop()
    else:
        if auto_update_job_id:
            # Cancela la próxima ejecución programada
            root.after_cancel(auto_update_job_id)
            auto_update_job_id = None
            print("Actualización automática detenida.")

# --- CREACIÓN DE LA INTERFAZ GRÁFICA (GUI) ---

# Ventana principal
root = tk.Tk()
root.title("Generador de Clima HTML")
root.geometry("380x250") # Tamaño inicial de la ventana (un poco más alto)
root.resizable(False, False) # Evitar que se pueda cambiar el tamaño

# Frame principal para organizar los widgets
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill="both", expand=True)

# Etiqueta y campo de entrada para la ciudad
ttk.Label(main_frame, text="Ciudad:").grid(row=0, column=0, sticky="w", pady=5)
city_entry = ttk.Entry(main_frame, width=30)
city_entry.grid(row=0, column=1, sticky="ew")
city_entry.insert(0, "El Progreso, HN") # Valor por defecto

# Etiqueta y menú desplegable para las unidades
ttk.Label(main_frame, text="Unidades:").grid(row=1, column=0, sticky="w", pady=5)
units_var = tk.StringVar(value="metric") # Variable para almacenar la selección
units_menu = ttk.Combobox(main_frame, textvariable=units_var, values=["metric (Celsius)", "imperial (Fahrenheit)"], state="readonly")
units_menu.grid(row=1, column=1, sticky="ew")
# Simplificamos el valor guardado para que coincida con la API
units_menu.bind('<<ComboboxSelected>>', lambda event: units_var.set(units_var.get().split(' ')[0]))

# Checkbox para la actualización automática
auto_update_var = tk.BooleanVar()
auto_update_check = ttk.Checkbutton(main_frame, 
                                    text="Auto-actualizar cada 15 minutos", 
                                    variable=auto_update_var,
                                    command=toggle_auto_update)
auto_update_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

# Botón para generar el reporte
generate_button = ttk.Button(main_frame, text="Generar HTML Ahora", command=obtener_y_actualizar_clima)
generate_button.grid(row=3, column=0, columnspan=2, pady=10)

# Iniciar el bucle principal de la aplicación
root.mainloop()
