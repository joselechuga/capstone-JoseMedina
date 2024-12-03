import os
import requests
import logging
import time
import sys

# directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fecha = time.strftime("%Y-%m-%d")



# RUTA DIRECTORIO DE LOGS 
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configurar el logging
logging.basicConfig(
    filename=os.path.join(log_dir, f'{fecha}.lst'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django

django.setup()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from busqueda import desplegar_tabla, buscar_en_tabla, buscar_y_hacer_clic_enlace, buscar_elemento_por_palabra

from modulos.views import add_cliente, add_unidad, add_documento, add_coincidencias
from modulos.escaneado import eliminar_contenido_directorio, mostrar_contenido_archivo


#RUTAS DE DESCARGA
current_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(current_dir, 'Descargas')


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
    options = webdriver.ChromeOptions()
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
    
def renombrar_archivo_descargado(id_fiscalizable):
    global download_dir  # Usa global si necesitas modificarla
    time.sleep(5)  # Ajusta el tiempo según sea necesario

    for filename in os.listdir(download_dir):
        if filename.endswith(".crdownload"):
            continue
        file_path = os.path.join(download_dir, filename)

        if id_fiscalizable in filename:
            nombre_archivo = os.path.basename(file_path)
            print(f"Archivo descargado: {nombre_archivo}")
            logging.info(f"Archivo descargado: {nombre_archivo}")

            nuevo_nombre = f"{id_fiscalizable}.pdf"
            nuevo_path = os.path.join(download_dir, nuevo_nombre)
            os.rename(file_path, nuevo_path)
            print(f"Archivo renombrado a: {nuevo_nombre}")
            logging.info(f"Archivo renombrado a: {nuevo_nombre}")
            break
        else:
            print(f"Archivo {filename} no coincide con el patrón esperado y será ignorado.")
            logging.info(f"Archivo {filename} no coincide con el patrón esperado y será ignorado.")


def verificar_descarga_correcta(nombre_documento):
    global download_dir  # Usa global si necesitas modificarla
    try:
        archivos = os.listdir(download_dir)
        for archivo in archivos:
            if nombre_documento in archivo:
                print(f"El archivo {archivo} se descargó correctamente.")
                logging.info(f"El archivo {archivo} se descargó correctamente.")
                return True
        print(f"No se encontró el archivo {nombre_documento} en el directorio de descargas.")
        logging.info(f"No se encontró el archivo {nombre_documento} en el directorio de descargas.")
        return False
    except Exception as e:
        print(f"Error al verificar la descarga del archivo: {e}")
        logging.info(f"Error al verificar la descarga del archivo: {e}")
        return False
                        


def interactuar_con_pagina(driver):
    try:
        logging.info("**************************")
        logging.info(f"Iniciando Scraping . . .")
        driver.get("https://snifa.sma.gob.cl/Fiscalizacion")

        # Esperar a que el modal de carga desaparezca
        esperar_modal_desaparecer(driver)

        # Inicializa el progreso
        total_filas = 100
        progreso_actual = 0

        download_dir = os.path.join(current_dir, 'Descargas')

        # Contador para el mensaje de no más filas
        no_more_rows_count = 0

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
            EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr"))
        )
        
        # Esperar a que el modal de carga desaparezca antes de interactuar con la tabla
        esperar_modal_desaparecer(driver)

        filas = driver.find_elements(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr")
        logging.info(f"Cargando resultados")
        esperar_modal_desaparecer(driver)

        url_resultados = driver.current_url

        logging.info(f"Desplegando todos los resultados")
        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/div[4]/select/option[7]"))
        ).click()

        num_filas = len(driver.find_elements(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr"))
        for i in range(num_filas):
            try:
                # Esperar a que el modal de carga desaparezca antes de cada interacción
                esperar_modal_desaparecer(driver)

                filas = driver.find_elements(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr")
                if i < len(filas):
                    no_more_rows_count = 0  # Reinicia el contador si se procesa una fila

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
                    
                    desplegar_tabla(driver)
                    elemento = buscar_elemento_por_palabra(driver, "Informe de Fiscalización Ambiental")
                    
                    if elemento:
                        buscar_y_hacer_clic_enlace(driver, elemento)

                        # Renombrar el archivo descargado
                        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Descargas')
                        nombre_documento = "IFA_" + unidad_fiscalizable
                        #renombrar_archivo_descargado(download_dir, id_fiscalizable)

                    # Verificar si el archivo se descargó correctamente
                    if verificar_descarga_correcta(nombre_documento):
                        print("La descarga del archivo fue exitosa.")
                        logging.info("La descarga del archivo fue exitosa.")
                    else:
                        print("La descarga del archivo falló.")
                        logging.info("La descarga del archivo falló.")

    
                    mostrar_contenido_archivo()

                    coincidencias = mostrar_contenido_archivo()
                    
                    # Añadir datos a las tablas
                    
                    # TABLA CLIENTES
                    add_cliente(clientes)
                    
                    #TABLA UNIDAD FISCALIZABLE
                    add_unidad(unidad_fiscalizable, ubicacion, url_pagina_actual, clientes)
                    
                    # TABLA DOCUMENTO
                    add_documento(url_pagina_actual, unidad_fiscalizable, nombre_documento)
                    
                    # TABLA COINCIDENCIAS
                    
                    #for i, palabra in enumerate(coincidencias):
                    #   logging.info(f"Datos para coincidencias: cantidad={i}, url_documento={url_pagina_actual}, palabras={palabra}")
                    #  add_coincidencias(i, url_pagina_actual, palabra)

                    
                    add_coincidencias(coincidencias[1][0], url_pagina_actual, coincidencias[0][1])

                    # Volver a la pagina de tabla de resultados
                    regresar_a_pagina_anterior(driver)

                    # Actualiza el progreso
                    progreso_actual = int((i + 1) / total_filas * 100)
                    actualizar_progreso(progreso_actual)
                    
                    # ELIMINAR CONTENIDO DE LA CARPET DESCARGAS
                    eliminar_contenido_directorio(download_dir)

                    # Cambiar al contexto de la nueva pestaña si se abre una
                    driver.switch_to.window(driver.window_handles[-1])

                    # Realizar acciones en la nueva pestaña
                    # ...

                    # Cerrar la pestaña emergente después de realizar las acciones necesarias
                    cerrar_pestana_actual(driver)

                    # Volver al contexto de la pestaña original
                    if len(driver.window_handles) > 0:
                        driver.switch_to.window(driver.window_handles[0])

                else:
                    logging.info(f"No hay más filas para procesar en el índice {i}")
                    no_more_rows_count += 1  # Incrementa el contador

                    # Si el mensaje aparece 3 veces seguidas, cierra el proceso
                    if no_more_rows_count >= 3:
                        print("El proceso se cerrará automáticamente después de 3 intentos fallidos.")
                        logging.info("El proceso se cerrará automáticamente después de 3 intentos fallidos.")
                        cerrar_navegador(driver)
                        return

                    regresar_a_pagina_anterior(driver)  # Intentar volver a la página anterior

            except Exception as e:
                if "no such window" in str(e):
                    print("La ventana del navegador fue cerrada manualmente.")
                    logging.info("La ventana del navegador fue cerrada manualmente.")
                    logging.info("**************************")
                    break
                else:
                    print(f"Error al procesar la fila {i + 1}: {e}")
                    logging.info(f"Error al procesar la fila {i + 1}: {e}")
                    regresar_a_pagina_anterior(driver)

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
            EC.invisibility_of_element_located((By.ID, "cargandoInformacion"))
        )
        print("El modal ha desaparecido")
        logging.info("El modal ha desaparecido")
    except Exception as e:
        print(f"Error al esperar que el modal desaparezca: {e}")
        logging.info(f"Error al esperar que el modal desaparezca: {e}")


def cerrar_pestana_actual(driver):
    try:
        # Imprimir las ventanas activas
        print("Ventanas activas antes de cerrar:", driver.window_handles)
        logging.info(f"Ventanas activas antes de cerrar: {driver.window_handles}")

        # Cierra la pestaña actual
        driver.close()
        print("Pestaña cerrada exitosamente.")
        logging.info("Pestaña cerrada exitosamente.")

        # Imprimir las ventanas activas después de cerrar
        print("Ventanas activas después de cerrar:", driver.window_handles)
        logging.info(f"Ventanas activas después de cerrar: {driver.window_handles}")
    except Exception as e:
        print(f"Error al cerrar la pestaña: {e}")
        logging.info(f"Error al cerrar la pestaña: {e}")

def main():
    try:
        logging.info('Proceso iniciado')
        # Código principal
        # ...
        logging.info('Proceso completado correctamente')
    except Exception as e:
        logging.error(f'Error en el proceso: {e}')
    finally:
        logging.info('Proceso cerrado manualmente')

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    driver = iniciar_driver()
    interactuar_con_pagina(driver)