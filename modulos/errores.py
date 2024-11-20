import time
import os
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By




fecha = time.strftime("%Y-%m-%d")

# Asegúrate de que el directorio de logs existe
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configurar el logging
logging.basicConfig(filename=os.path.join(log_dir, f'{fecha}.lst'), level=logging.INFO)

def monitorear_carga_pagina(driver):
    """
    Monitorea la carga de páginas y reconoce si ocurre un error "504 Gateway Time-out".
    
    Args:
        driver (webdriver): El controlador del navegador.
    
    Returns:
        bool: True si se detecta un "504 Gateway Time-out", False en caso contrario.
    """
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return False
    except TimeoutException as e:
        mensaje_error = str(e)
        if "504 Gateway Time-out" in mensaje_error and "The server didn't respond in time." in mensaje_error:
            print("Error 504 Gateway Time-out detectado.")
            logging.info("Error 504 Gateway Time-out detectado.")
            return True
        return False
