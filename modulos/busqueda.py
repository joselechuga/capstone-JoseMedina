import logging
import os
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchWindowException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

fecha = time.strftime("%Y-%m-%d")

# Asegúrate de que el directorio de logs existe
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configurar el logging
logging.basicConfig(filename=os.path.join(log_dir, f'{fecha}.lst'), level=logging.INFO)

def desplegar_tabla(driver):
    """Da clic en el path especificado para desplegar la tabla de búsqueda."""
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div/div/div[2]/div[1]/div[1]/h4/a"))
        ).click()
        print("Tabla de búsqueda desplegada.")
        logging.info("Tabla de búsqueda desplegada.")
    except TimeoutException:
        print("No se pudo encontrar el elemento para desplegar la tabla de búsqueda.")
        logging.info("No se pudo encontrar el elemento para desplegar la tabla de búsqueda.")
    except Exception as e:
        print(f"Error inesperado al intentar desplegar la tabla de búsqueda: {e}")
        logging.info(f"Error inesperado al intentar desplegar la tabla de búsqueda: {e}")

def buscar_en_tabla(driver, palabra):
    """Busca y recorre la tabla en el path especificado y busca un elemento mediante la función 'buscar_elemento_por_palabra'."""
    try:
        # Esperar hasta que la tabla esté presente
        tabla = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div/div/div[2]/div[1]/div[2]/div/table"))
        )
        filas = tabla.find_elements(By.XPATH, ".//tr")
        
        for fila in filas:
            try:
                # Buscar el elemento en la fila actual
                elemento = buscar_elemento_por_palabra(driver, palabra)
                if elemento:
                    #print(f"Elemento encontrado en la fila: {fila.text}")
                    #logging.info(f"Elemento encontrado en la fila: {fila.text}")
                    
                    # Intentar hacer clic en el enlace de la misma fila
                    if buscar_y_hacer_clic_enlace(driver, elemento):
                        print("Enlace clicado y archivo descargado.")
                        logging.info("Enlace clicado y archivo descargado.")
                    return elemento
            except Exception as e:
                print(f"Error al buscar en la fila: {e}")
                logging.info(f"Error al buscar en la fila: {e}")
        
        print("No se encontró el elemento en ninguna fila de la tabla.")
        logging.info("No se encontró el elemento en ninguna fila de la tabla.")
        return None
    except TimeoutException:
        print("No se pudo encontrar la tabla en el path especificado.")
        logging.info("No se pudo encontrar la tabla en el path especificado.")
        return None
    except Exception as e:
        print(f"Error inesperado al buscar en la tabla: {e}")
        logging.info(f"Error inesperado al buscar en la tabla: {e}")
        return None

def buscar_elemento_por_palabra(driver, palabra):
    """Busca un elemento en la página que contenga exactamente la frase 'Informe de Fiscalización Ambiental'."""
    try:
        elementos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, f"//*[text()='{palabra}']"))
        )
        for elemento in elementos:
            print(f"Elemento encontrado con la palabra exacta: {palabra}")
            logging.info(f"Elemento encontrado con la palabra exacta: {palabra}")
            return elemento
        print(f"No se encontró ningún elemento con la palabra exacta: {palabra}")
        logging.info(f"No se encontró ningún elemento con la palabra exacta: {palabra}")
        return None
    except TimeoutException:
        print(f"No se encontró ningún elemento con la palabra exacta: {palabra}")
        logging.info(f"No se encontró ningún elemento con la palabra exacta: {palabra}")
        return None
    except Exception as e:
        print(f"Error inesperado al buscar el elemento con la palabra exacta '{palabra}': {e}")
        logging.info(f"Error inesperado al buscar el elemento con la palabra exacta '{palabra}': {e}")
        return None

def buscar_y_hacer_clic_enlace(driver, elemento):
    """Hace clic en el enlace en la misma fila del elemento encontrado previamente."""
    try:
        # Encontrar el enlace en la misma fila del elemento
        link_element = elemento.find_element(By.XPATH, "../td[4]/a")
        download_url = link_element.get_attribute('href')
        print(f"Elemento encontrado previamente. URL del enlace: {download_url}")
        logging.info(f"Elemento encontrado previamente. URL del enlace: {download_url}")

        # Aumentar el tiempo de espera para el clic
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable(link_element))

        # Hacer clic en el enlace
        link_element.click()
        return True
    except TimeoutException:
        print("Tiempo de espera agotado al intentar hacer clic en el enlace.")
        logging.info("Tiempo de espera agotado al intentar hacer clic en el enlace.")
        return False
    except NoSuchWindowException:
        print("La ventana del navegador fue cerrada inesperadamente.")
        logging.info("La ventana del navegador fue cerrada inesperadamente.")
        return False
    except Exception as e:
        print(f"Error al intentar hacer clic en el enlace de la fila: {e}")
        logging.info(f"Error al intentar hacer clic en el enlace de la fila: {e}")
        return False
