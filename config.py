# ==============================================================================
# CONFIGURACIÓN CENTRALIZADA
# ==============================================================================

import os

# Rutas
CHROMEDRIVER_PATH = "C:\\Users\\Noval\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# NOTA: Las credenciales ahora se manejan a través del módulo login.py
# que solicita las credenciales al usuario de forma interactiva y segura

# Usuarios de ejemplo (solo para referencia o pruebas rápidas)
# NOTA: El sistema principal obtiene usuarios desde la base de datos
# Estos usuarios solo se usan si eliges la opción "lista específica" en el scraper
USERNAMES_EJEMPLO = [
    'instagram',
    'cristiano', 
    'leomessi',
    'nasa',
    'selenagomez',
    'kyliejenner',
    'justinbieber',
    'taylorswift'
]

# Configuración de scraping
SCRAPING_CONFIG = {
    'delay_min': 2,      # Delay mínimo entre requests (segundos)
    'delay_max': 6,      # Delay máximo entre requests (segundos)
    'max_retries': 3,    # Máximo número de reintentos
    'timeout': 20,       # Timeout para requests
    'headless': True,    # Ejecutar Chrome sin ventana visible
    'force_rescrape': False,  # Si True, scrapea incluso perfiles ya completos
}

# Archivos de salida
OUTPUT_CONFIG = {
    'save_csv': True,  # Si guardar archivo CSV
    'csv_file': 'instagram_profiles.csv',
    'database_file': 'instagram_data.db',  # Archivo de base de datos
}

# No necesitamos crear directorios adicionales