import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchWindowException
import subprocess
import logging  # Importa el módulo logging para registrar información en un archivo de registro

# Suponiendo que 'fecha' es una variable que contiene la fecha actual en el formato deseado
fecha = time.strftime("%Y-%m-%d")

# Asegúrate de que el directorio de logs existe
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=os.path.join(log_dir, f'{fecha}.lst'), level=logging.INFO)

# Añade el directorio raíz del proyecto al PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from odorwatch.models import UnidadFiscalizable 
from modulos.views import add_cliente, add_unidad, add_documento

current_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(current_dir, 'Descargas')

def setup_driver():
    """Inicializa el WebDriver con la ruta de descarga."""
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    return driver

def process_first_category(driver):
    
    logging.info('Iniciando Scraping...')
    
    """Realiza la búsqueda en la primera categoría y descarga los documentos fila por fila."""
    base_url = 'https://snifa.sma.gob.cl/Fiscalizacion'
    
    try:
        driver.get(base_url)
    except NoSuchWindowException:
        logging.info("La ventana del navegador se cerró inesperadamente. Reiniciando el WebDriver.")
        driver = setup_driver()
        driver.get(base_url)

    if not check_page_load(driver):
        return

    select_category(driver)
    wait_for_modal_to_disappear(driver)
    wait = WebDriverWait(driver, 10)
    # filas que recorrerá de la tabla principal
    i = 1
    while True:
        try:
            row_xpath = f"//table/tbody/tr[{i}]"
            row = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
            logging.info(f"""Procesando fila {i}...""")
            process_row(driver, row, i)
            i += 1
        except TimeoutException:
            logging.info(f"No se pudo encontrar la fila {i}, terminando proceso.")
            break
        except NoSuchWindowException:
            logging.info("La ventana del navegador se cerró inesperadamente durante el procesamiento de filas.")
            break

# SELECCION DE CATEGORIA Y CLIC EN BUSCAR
def select_category(driver):
    """Selecciona la categoría 'Agroindustrias' y hace clic en el botón de buscar."""
    try:
        wait = WebDriverWait(driver, 20)# esperar a que desaparezca el modal en 20 seg
        category_select = wait.until(EC.presence_of_element_located((By.ID, "categoria"))) #busqueda del selector categoria
        category_select.click() # clic en el selector

        agroindustria_option = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='categoria']/option[@value='6']")))
        agroindustria_option.click()

        logging.info("Categoría 'Agroindustrias' seleccionada.")
        buscar_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Buscar')]")))
        buscar_button.click()
        logging.info("Clic en el botón 'Buscar'.")

    except TimeoutException:
        logging.info("Error al seleccionar la categoría o hacer clic en buscar.")
    except Exception as e:
        logging.info(f"Error inesperado: {e}")

def click_next_button(driver):
    """Da clic en el siguiente botón después de que desaparezca el modal inicial."""
    try:
        wait = WebDriverWait(driver, 30)
        wait_for_modal_to_disappear(driver)
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/div[4]/select/option[7]")))
        next_button.click()
        logging.info("Clic en el siguiente botón.")
    except TimeoutException:
        logging.info("Error al intentar hacer clic en el siguiente botón.")
    except Exception as e:
        logging.info(f"Error inesperado: {e}")


####################################################################
####################################################################
# FUNCIONES DE UTILIDAD DE ACCION Y CONTROL DE LAS DEMAS FUNCIONES
#def logging.info(message):
#    """Guarda la actividad en un archivo de log."""
# log_file_path = os.path.join(os.getcwd(), "logs_scraping.txt")
# with open(log_file_path, "a") as log_file:
#     log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
# print(message)

def log_error(error_message):
    """Guarda el error en un archivo de log."""
    log_file_path = os.path.join(os.getcwd(), "error_log.txt")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")
    print(f"Error registrado: {error_message}")

def wait_for_modal_to_disappear(driver, timeout=30):
    """Espera a que el modal desaparezca."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "cargandoInformacion"))
        )
        logging.info("El modal de carga ha desaparecido.")
    except TimeoutException:
        logging.info("El modal no desapareció a tiempo.")

def check_page_load(driver):
    """Verifica si la página se cargó correctamente y no hubo errores."""
    try:
        page_error = driver.find_element(By.TAG_NAME, "h1").text
        if "504" in page_error:
            error_message = f"Carga de página errónea por: {page_error}"
            log_error(error_message)
            close_driver(driver)
            return False
        return True
    except NoSuchElementException:
        return True

###################################################################################
###################################################################################
# cambiar path
def extract_expediente_id(driver):
    """Extrae el ID de expediente de la etiqueta <h3> dentro del div específico."""
    try:
        panel_expediente = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.panel.panel-default.panel-expediente.panel-expediente1 h3"))
        )
        expediente_text = panel_expediente.text
        if "Expediente" in expediente_text:
            ID_unidad_fiscalizable = expediente_text.replace("Expediente: ", "").strip()
            logging.info(f"ID de unidad fiscalizable extraído: {ID_unidad_fiscalizable}")
            return ID_unidad_fiscalizable
        else:
            logging.info("La etiqueta <h3> no contiene 'Expediente'.")
            return None
    except TimeoutException:
        logging.info("No se encontró el elemento 'Expediente' en el div especificado.")
        return None

def get_ubicacion(driver):
    """Extrae la ubicación de la unidad fiscalizable."""
    try:
        ubicacion_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(., 'Región')]"))
        )
        ubicacion_u_fiscalizable = ubicacion_element.text.split("Región")[1].strip()
        logging.info(f"Ubicación extraída: {ubicacion_u_fiscalizable}")
        return ubicacion_u_fiscalizable
    except TimeoutException:
        logging.info("No se pudo encontrar la ubicación.")
        return None

# obtener nombre de la unidad fiscalizable
def get_nombre_u_fiscalizable(driver):
    logging.info("""Extrayendo el nombre de la unidad fiscalizable...""")
    try:
        nombre_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div/div[2]/div/div/div/div[1]/div/ul/li/a"))
        )
        nombre_u_fiscalizable = nombre_element.text.strip()
        logging.info(f"Nombre de unidad fiscalizable extraído: {nombre_u_fiscalizable}")
        return nombre_u_fiscalizable
    except TimeoutException:
        logging.info("No se pudo encontrar el nombre de la unidad fiscalizable.")
        return None

# guardar id de la unidad fiscalizable en la base de datos
def save_unidad_fiscalizable(driver, ID_unidad_fiscalizable):
    """Guarda la unidad fiscalizable en la base de datos."""
    ubicacion = get_ubicacion(driver)
    nombre = get_nombre_u_fiscalizable(driver)
    
    if ID_unidad_fiscalizable and ubicacion and nombre:
        unidad_fiscalizable = UnidadFiscalizable(
            id=ID_unidad_fiscalizable,
            nombre=nombre,
            ubicacion=ubicacion,
            url=driver.current_url,
            cliente_id=ID_unidad_fiscalizable
        )
        unidad_fiscalizable.save()
        logging.info(f"Unidad Fiscalizable '{nombre}' guardada en la base de datos.")
    else:
        logging.info("No se pudo guardar la Unidad Fiscalizable debido a datos incompletos.")

# guardar año de ejecucion del informe
def get_año_ejecucion(driver):
    """Extrae el año de ejecución del informe."""
    try:
        año_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div/div[1]/div/div/h4[3]/text()"))
        )
        año_ejecucion = año_element.text.strip()
        logging.info(f"Año de ejecución extraído: {año_ejecucion}")
        return año_ejecucion
    except TimeoutException:
        logging.info("No se pudo encontrar el año de ejecución.")
        return None
    except Exception as e:
        logging.info(f"Error inesperado al intentar extraer el año de ejecución: {e}")
        return None


# clic en drop de documentos
def click_documentos_tab(driver):
    """Hace clic en la pestaña de documentos."""
    try:
        documentos_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/div/div/div/div[2]/div[1]/div[1]/h4/a"))
        )
        documentos_tab.click()
        logging.info("Clic en la pestaña 'Documentos'.")
    except TimeoutException:
        logging.info("No se pudo hacer clic en la pestaña 'Documentos'.")

# Expandir seccion de documentos para 
def expand_document_section(driver):
    """Expande la sección de Documentos si está colapsada."""
    try:
        document_section = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='accordion-toggle' and @data-toggle='collapse' and @href='#collapse-documentos']"))
        )
        document_section.click()
        logging.info("Sección 'Documentos' expandida.")
    except TimeoutException:
        logging.info("No se pudo expandir la sección 'Documentos'.")
    except Exception as e:
        logging.info(f"Error inesperado al intentar expandir la sección 'Documentos': {e}")

# Recorrer las filas de la tabla de documentos
def process_document_table(driver, ID_unidad_fiscalizable, search_phrase):
    """Recorre las filas de la tabla y descarga los documentos que correspondan."""
    try:
        expand_document_section(driver)
    except:
        logging.info("No se encontró acordeon")
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'tabla-resultado-busqueda')]/tbody/tr"))
    )
    
    # Recorre las filas de la tabla
    rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'tabla-resultado-busqueda')]/tbody/tr")
    for row in rows:
        try:
            # Verificar si la fila contiene el texto "Informe de Fiscalización Ambiental"
            cell_element = buscar_elemento_por_palabra(driver, "Informe de Fiscalización Ambiental")
            cell_text = cell_element.text if cell_element else ""
            logging.info(f"CELDA {cell_text}")
            if "Informe de Fiscalización Ambiental" in cell_text:
                try:
                    # Intentar obtener el enlace de descarga usando cell_element
                    link_element = cell_element.find_element(By.XPATH, "../td[4]/a")
                    download_url = link_element.get_attribute('href')
                    document_name = "Informe de Fiscalización Ambiental"
                    
                    # Extraer el nombre de la unidad fiscalizable
                    nombre_unidad = get_nombre_u_fiscalizable(driver)
                    
                    if nombre_unidad:
                        download_document(driver, download_url, document_name, ID_unidad_fiscalizable, nombre_unidad)
                        if "Anexo" not in document_name and "ANEXO" not in document_name and not download_url.endswith('.zip'):
                            logging.info(f"Documento '{document_name}' descargado y procesado.")
                except NoSuchElementException:
                    logging.info("No se pudo encontrar el enlace de descarga, reintentando con cell_element...")
                    continue  # Volver a intentar encontrar el enlace
        except NoSuchElementException as e:
            logging.info(f"Error al procesar la fila de la tabla: {e}")

def buscar_elemento_por_palabra(driver, palabra):
    """Busca un elemento en la página que contenga exactamente la frase 'Informe de Fiscalización Ambiental'."""
    try:
        elementos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, f"//*[text()='{palabra}']"))
        )
        for elemento in elementos:
            logging.info(f"Elemento encontrado con la palabra exacta: {palabra}")
            return elemento
        logging.info(f"No se encontró ningún elemento con la palabra exacta: {palabra}")
        return None
    except TimeoutException:
        logging.info(f"No se encontró ningún elemento con la palabra exacta: {palabra}")
        return None
    except Exception as e:
        logging.info(f"Error inesperado al buscar el elemento con la palabra exacta '{palabra}': {e}")
        return None

# descargar documento en formato PDF con ID de U.Fiscalizable
def download_document(driver, download_url, document_name, ID_unidad_fiscalizable, nombre_unidad):
    """Descarga el documento en formato PDF con un nombre personalizado y sobrescribe si existe. Luego, escanea el documento en busca de palabras clave."""
    try:
        # Obtener la URL de la página actual
        current_page_url = driver.current_url
        logging.info(f"URL de la página donde se encuentra el documento: {current_page_url}")

        # Asegurarse de que todos los documentos contengan el ID de unidad fiscalizable en el nombre
        if not document_name.endswith(f"_{ID_unidad_fiscalizable}"):
            document_name = f"{document_name}_{ID_unidad_fiscalizable}"
        
        file_name = f"{document_name}.pdf"
        file_path = os.path.join(download_dir, file_name)

        # Si el archivo existe se sobrescribe
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Archivo {file_name} ya existe y será reemplazado.")

        response = requests.get(download_url, stream=True)
        with open(file_path, 'wb') as file:
            file.write(response.content)

        logging.info(f"Documento descargado como: {file_name}")
        logging.info(nombre_unidad)
        
        # Guardar el documento en la base de datos
        add_documento(current_page_url, nombre_unidad, file_name)
        
        # Verificar si el archivo está completo
        if not is_pdf_complete(file_path):
            logging.info(f"El documento {file_name} está incompleto o corrupto. Intentando descargar de nuevo...")
            os.remove(file_path)
            return

        # Iniciar funciones del documento escaneado.py para el archivo recién descargado
        from modulos.escaneado import buscar_palabras, procesar_documentos
        contenido = procesar_documentos(download_dir)
        buscar_palabras(contenido, file_name)

    except Exception as e:
        logging.info(f"Error al descargar el documento: {e}")

def is_pdf_complete(file_path):
    """Verifica si el archivo PDF está completo."""
    try:
        from PyPDF2 import PdfReader
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            # Intentar leer el documento para verificar su integridad
            reader.pages
        return True
    except Exception as e:
        logging.info(f"Error al verificar el documento PDF: {e}")
        return False

def scan_palabras(file_path):
    """Abre el documento PDF y analiza su contenido en busca de palabras clave desde el modelo 'Palabras'. Elimina el documento si no contiene ninguna."""
    logging.info('Escaneando archivos en busca de palabras clave...')
    try:
        from PyPDF2 import PdfReader
        from odorwatch.models import Palabras

        # Obtener todas las palabras clave desde el modelo Palabras
        palabras_clave = Palabras.objects.all().values_list('palabras', flat=True)

        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if any(palabra in text for palabra in palabras_clave):
                    return True
        # Si no se encuentran palabras clave, eliminar el archivo
        os.remove(file_path)
        logging.info(f"Documento {file_path} eliminado por no contener palabras clave.")
        return False
    except Exception as e:
        logging.info(f"Error al escanear el documento: {e}")
        return False

# obtener nombre del cliente
def get_cliente_nombre(driver, i):
    """Extrae el nombre del cliente desde la tabla de resultados."""
    try:
        cliente_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div[4]/div/div/div/div/div[2]/div[3]/table/tbody/tr[{i}]/td[3]/ul/li"))
        )
        logging.info(f"FILAS: {i}")
        nombre_cliente = cliente_element.text.strip()
        logging.info(f"Nombre del cliente extraído: {nombre_cliente}")
        return nombre_cliente
    except TimeoutException:
        logging.info("No se pudo encontrar el nombre del cliente.")
        return None
    except NoSuchElementException:
        logging.info("No se encontró el elemento del nombre del cliente.")
        return None
    except Exception as e:
        logging.info(f"Error inesperado al extraer el nombre del cliente: {e}")
        return None

# proceso en la primera tabla
def process_row(driver, row, i):
    """Procesa una fila de la tabla y descarga el documento correspondiente."""
    # espera a que desaparezca el modal emergente
    wait = WebDriverWait(driver, 20)  # 20 segundos
    
    # Extrae y guarda el nombre del cliente
    nombre_cliente = get_cliente_nombre(driver, i)
    if nombre_cliente:
        resultado = add_cliente(nombre_cliente)
        logging.info(resultado)
    
    detalle_link = row.find_element(By.XPATH, ".//a[contains(text(),'Ver detalle')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", detalle_link)
    logging.info("Scroll hacia el enlace 'Ver detalle'.")
    
    # Esperar a que el modal desaparezca antes de hacer clic
    wait_for_modal_to_disappear(driver)
    
    try:
        detalle_link.click()
        logging.info("Clic en el enlace 'Ver detalle'.")
    except ElementClickInterceptedException:
        logging.info("El clic en el enlace 'Ver detalle' fue interceptado. Intentando de nuevo...")
        wait_for_modal_to_disappear(driver)
        detalle_link.click()
    
    # esperar a que desaparezca el modal emergente
    wait_for_modal_to_disappear(driver)
    # parámetros para unidad fiscalizable
    nombre_unidad, ubicacion_unidad, url_unidad = get_unidad(driver)
    if nombre_unidad and ubicacion_unidad and url_unidad:
        resultado = add_unidad(nombre_unidad, ubicacion_unidad, url_unidad, nombre_cliente)
        logging.info(resultado)
    logging.info(f"NOMBRE U F: {nombre_unidad}")
    # Extraer ID para unidad fiscalizable
    try:
        id_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div/div[1]/div/div/h3"))
        )
        ID_unidad_fiscalizable = id_element.text.strip()[12:]
        logging.info(f"ID de unidad fiscalizable extraído: {ID_unidad_fiscalizable}")
    except TimeoutException:
        logging.info("No se pudo encontrar el ID de la unidad fiscalizable.")
        ID_unidad_fiscalizable = None
    except NoSuchElementException:
        logging.info("No se encontró el elemento del ID de la unidad fiscalizable.")
        ID_unidad_fiscalizable = None
    except Exception as e:
        logging.info(f"Error inesperado al extraer el ID de la unidad fiscalizable: {e}")
        ID_unidad_fiscalizable = None

    # save_unidad_fiscalizable(driver, ID_unidad_fiscalizable)
    click_documentos_tab(driver)
    documento = "Informe de Fiscalización Ambiental"
    logging.info(nombre_unidad)
    process_document_table(driver, ID_unidad_fiscalizable, documento)
    driver.back()
    logging.info("Volviendo a la página de resultados.")
    if ID_unidad_fiscalizable:
        print(f"ID Unidad Fiscalizable: {ID_unidad_fiscalizable}")


# recolectar datos para tabla 'UFiscal'
def get_unidad(driver):
    """Extrae el nombre, la ubicación y la URL de la unidad fiscalizable."""
    try:
        # Extraer el nombre y la URL
        nombre_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div/div[2]/div/div/div/div[1]/div/ul/li/a"))
        )
        nombre = nombre_element.text.strip()
        url = nombre_element.get_attribute('href')
        logging.info(f"Nombre extraído: {nombre}")
        logging.info(f"URL extraída: {url}")

        # Extraer la ubicación
        ubicacion_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div/div[2]/div/div/div/div[1]/div/ul/li"))
        )
        ubicacion_text = ubicacion_element.text.strip()
        ubicacion = ubicacion_text.split('-')[-1].strip() if '-' in ubicacion_text else ubicacion_text
        logging.info(f"Ubicación extraída: {ubicacion}")

        return nombre, ubicacion, url

    except TimeoutException:
        logging.info("No se pudo encontrar uno de los elementos necesarios.")
        return None, None, None
    except NoSuchElementException:
        logging.info("No se encontró uno de los elementos necesarios.")
        return None, None, None
    except Exception as e:
        logging.info(f"Error inesperado al extraer los datos de la unidad: {e}")
        return None, None, None


def close_driver(driver):
    """Cierra el WebDriver."""
    driver.quit()
    
def main():
    driver = setup_driver()
    try:
        process_first_category(driver)
    finally:
        close_driver(driver)
        logging.info("Terminando scraping.")
        logging.info("***************************************")

if __name__ == '__main__':
    main()