import os
import requests
import logging
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from busqueda import desplegar_tabla, buscar_en_tabla, buscar_y_hacer_clic_enlace

# directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fecha = time.strftime("%Y-%m-%d")

# RUTA DIRECTORIO DE LOGS 
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configurar el logging
logging.basicConfig(filename=os.path.join(log_dir, f'{fecha}.lst'), level=logging.INFO)


# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django

django.setup()
from modulos.views import add_cliente, add_unidad, add_documento


def regresar_a_pagina_tabla(driver, url_resultados):
    driver.get(url_resultados)
    esperar_modal_desaparecer(driver)

def regresar_a_pagina_anterior(driver):
    driver.back()
    esperar_modal_desaparecer(driver)

def cerrar_navegador(driver):
    try:
        driver.quit()
        print("Navegador cerrado exitosamente.")
        logging.info("Navegador cerrado exitosamente.")
        logging.info("**************************")
    except Exception as e:
        print(f"Error al cerrar el navegador: {e}")
        logging.info(f"Error al cerrar el navegador: {e}")
        logging.info("**************************")

    
def iniciar_driver():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    options = webdriver.ChromeOptions()
    download_dir = os.path.join(current_dir, 'Descargas')
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(180)
    return driver
    
def renombrar_archivo_descargado(download_dir, nombre_documento):
    # Esperar a que el archivo se descargue completamente
    time.sleep(5)  # Ajusta el tiempo según sea necesario

    # Encuentra el archivo descargado
    for filename in os.listdir(download_dir):
        if filename.endswith(".crdownload"):  # Asegúrate de que el archivo se haya descargado completamente
            continue
        file_path = os.path.join(download_dir, filename)

        # Obtener solo el nombre del archivo
        nombre_archivo = os.path.basename(file_path)

        # Registrar el nombre del archivo sin cambiarlo
        print(f"Archivo descargado: {nombre_archivo}")
        logging.info(f"Archivo descargado: {nombre_archivo}")
        break

def interactuar_con_pagina(driver):
    try:
        logging.info("**************************")
        logging.info(f"Iniciando Scraping . . .")
        driver.get("https://snifa.sma.gob.cl/Fiscalizacion")

        # Inicializa el progreso
        total_filas = 100  # Suponiendo que hay 100 filas
        progreso_actual = 0

        # Actualiza barra de progreso en panel
        def actualizar_progreso(progreso):
            with open('progreso.txt', 'w') as f:
                f.write(str(progreso))
        with open('progreso.txt', 'w') as f:
            f.write('0')

        logging.info(f"Seleccionando categoria")

        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[1]/div/div[2]/div/div/form/div[2]/div/select/option[2]"))
        ).click()
        
        logging.info(f"Buscando . . .")
        
        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[1]/div/div[2]/div/div/form/button[2]"))
        ).click()

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr"))
        )

        esperar_modal_desaparecer(driver)

        url_resultados = driver.current_url

        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/div[4]/select/option[7]"))
        ).click()

        num_filas = len(driver.find_elements(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr"))
        for i in range(num_filas):
            try:
                filas = driver.find_elements(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr")
                if i < len(filas):
                    fila = filas[i]

                    id_fiscalizable = fila.find_element(By.XPATH, f"./td[2]").text
                    clientes = [cliente.text for cliente in fila.find_elements(By.XPATH, f"./td[3]/ul/li")]
                    unidad_fiscalizable = fila.find_element(By.XPATH, f"./td[5]/ul/li/a").text
                    ubicacion = fila.find_element(By.XPATH, f"./td[5]/ul/li/a").get_attribute("href")

                    # Convertir la lista de clientes a una cadena
                    clientes_str = ', '.join(clientes)

                    print(f"Fila {i + 1}:")
                    logging.info(f"--------------------")
                    logging.info(f"Fila {i + 1}:")
                    print(f"  Id_fiscalizable: {id_fiscalizable}")
                    logging.info(f"  Id_fiscalizable: {id_fiscalizable}")
                    print(f"  Clientes: {clientes_str}")
                    logging.info(f"  Clientes: {clientes_str}")
                    print(f"  Unidad_fiscalizable: {unidad_fiscalizable}")
                    logging.info(f"  Unidad_fiscalizable: {unidad_fiscalizable}")
                    print(f"  Ubicacion: {ubicacion}")
                    logging.info(f"  Ubicacion: {ubicacion}")

                    driver.execute_script("arguments[0].scrollIntoView();", fila.find_element(By.XPATH, f"./td[9]/a"))
                    fila.find_element(By.XPATH, f"./td[9]/a").click()

                    def recolectar_url_pagina(driver):
                        try:
                            url_actual = driver.current_url
                            print(f"URL actual de la página del documento: {url_actual}")
                            logging.info(f"URL actual de la página del documento: {url_actual}")
                            return url_actual
                        except Exception as e:
                            print(f"Error al recolectar la URL de la página: {e}")
                            logging.info(f"Error al recolectar la URL de la página: {e}")
                            return None

                    url_pagina_actual = recolectar_url_pagina(driver)
                    
                    # from escaneado import monitorear_ruta_descargas

                    
                    elemento = buscar_en_tabla(driver, "Informe de Fiscalización Ambiental")
                    desplegar_tabla(driver)
                    if elemento:
                        buscar_y_hacer_clic_enlace(driver, elemento)

                        # Renombrar el archivo descargado
                        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Descargas')
                        nombre_documento = "IFA_" + unidad_fiscalizable
                        renombrar_archivo_descargado(download_dir, nombre_documento)
                        #monitorear_ruta_descargas(driver)
                    # Añadir datos a las tablas
                    
                    # TABLA CLIENTES
                    add_cliente(clientes)
                    
                    #TABLA UNIDAD FISCALIZABLE
                    add_unidad(unidad_fiscalizable, ubicacion, url_pagina_actual, clientes)
                    
                    # TABLA DOCUMENTO
                    add_documento(url_pagina_actual, unidad_fiscalizable, nombre_documento)
                    
                    # Volver a la pagina de tabla de resultados
                    regresar_a_pagina_anterior(driver)

                    # Actualiza el progreso
                    progreso_actual = int((i + 1) / total_filas * 100)
                    actualizar_progreso(progreso_actual)

                else:
                    logging.info(f"No hay más filas para procesar en el índice {i}")

            except Exception as e:
                if "no such window" in str(e):
                    print("La ventana del navegador fue cerrada manualmente.")
                    logging.info("La ventana del navegador fue cerrada manualmente.")
                    logging.info("**************************")
                    break
                else:
                    print(f"Error al procesar la fila {i + 1}: {e}")
                    logging.info(f"Error al procesar la fila {i + 1}: {e}")

    except Exception as e:
        print(f"Error al interactuar con la página: {e}")
        logging.info(f"Error al interactuar con la página: {e}")
    finally:
        try:
            if driver.service.process:
                cerrar_navegador(driver)
        except Exception as e:
            print(f"Error al verificar el estado del navegador: {e}")
            logging.info(f"Error al verificar el estado del navegador: {e}")

def esperar_modal_desaparecer(driver):
    try:
        logging.info('Esperando a que desaparezca el modal')
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div"))
        )
        print("El modal ha desaparecido")
        logging.info("El modal ha desaparecido")
    except Exception as e:
        print(f"Error al esperar que el modal desaparezca: {e}")
        logging.info(f"Error al esperar que el modal desaparezca: {e}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    driver = iniciar_driver()
    interactuar_con_pagina(driver)