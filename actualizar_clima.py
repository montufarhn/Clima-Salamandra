import requests
import json
from datetime import datetime
from config import API_KEY # Importar la API Key desde config.py

# --- CONFIGURACIÓN ---
# Ciudad de la que quieres obtener el clima. Puedes cambiarla.
CIUDAD = 'El Progreso, HN' 
# Idioma de la descripción del clima (ej. 'es' para español, 'en' para inglés).
IDIOMA = 'es'
# Unidades ('metric' para Celsius, 'imperial' para Fahrenheit).
UNIDADES = 'metric'

# Nombres de los archivos
PLANTILLA_HTML = 'currenweather.html'
SALIDA_HTML = 'clima_actualizado.html'


def obtener_datos_clima():
    """Consulta la API de OpenWeatherMap y devuelve los datos del clima."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CIUDAD}&appid={API_KEY}&units={UNIDADES}&lang={IDIOMA}"
    try:
        response = requests.get(url)
        # Si la respuesta no es exitosa (ej. 404, 401), lanza un error.
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return None

def actualizar_html(datos_clima):
    """Lee la plantilla, reemplaza los marcadores y guarda el nuevo HTML."""
    if not datos_clima:
        print("No hay datos del clima para actualizar el HTML.")
        return

    try:
        with open(PLANTILLA_HTML, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Convertir timestamps de amanecer/atardecer a formato legible
        amanecer = datetime.fromtimestamp(datos_clima['sys']['sunrise']).strftime('%I:%M %p')
        atardecer = datetime.fromtimestamp(datos_clima['sys']['sunset']).strftime('%I:%M %p')

        # Reemplazar los marcadores con los datos de la API
        contenido = contenido.replace('[STATION]', datos_clima['name'])
        contenido = contenido.replace('[CONDITION]', datos_clima['weather'][0]['description'].capitalize())
        contenido = contenido.replace('[TEMP]', f"{datos_clima['main']['temp']:.1f}°C")
        contenido = contenido.replace('[FEELS]', f"{datos_clima['main']['feels_like']:.1f}°C")
        contenido = contenido.replace('[HUMIDITY]', f"{datos_clima['main']['humidity']}%")
        contenido = contenido.replace('[WIND]', f"{datos_clima['wind']['speed']} m/s")
        contenido = contenido.replace('[BAROMETER]', f"{datos_clima['main']['pressure']} hPa")
        contenido = contenido.replace('[SUNRISE AMPM]', amanecer)
        contenido = contenido.replace('[SUNSET AMPM]', atardecer)
        contenido = contenido.replace('[UPDATED]', f"Actualizado: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}")
        
        # El punto de rocío (Dew Point) no viene en la respuesta estándar de la API gratuita.
        contenido = contenido.replace('Dew Point: [DEW]<BR />', '') # Se elimina la línea

        with open(SALIDA_HTML, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"¡Éxito! El archivo '{SALIDA_HTML}' ha sido actualizado.")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de plantilla '{PLANTILLA_HTML}'.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    datos = obtener_datos_clima()
    actualizar_html(datos)
