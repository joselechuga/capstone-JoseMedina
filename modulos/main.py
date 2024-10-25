import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time

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

def close_driver(driver):
    """Cierra el WebDriver."""
    driver.quit()

def log_activity(message):
    """Guarda la actividad en un archivo de log."""
    log_file_path = os.path.join(os.getcwd(), "logs_scraping.txt")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

# Errores encontrados, son mostrados por consola
def log_error(error_message):
    """Guarda el error en un archivo de log."""
    log_file_path = os.path.join(os.getcwd(), "error_log.txt")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")
    print(f"Error registrado: {error_message}")

def wait_for_modal_to_disappear(driver, timeout=30):
    """Espera a que el modal desaparezca."""
    try:
        WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-body")))
        log_activity("El modal de carga ha desaparecido.")
    except TimeoutException:
        log_activity("El modal no desapareció a tiempo.")

def check_page_load(driver):
    """Verifica si la página se cargó correctamente y no hubo errores."""
    try:
        page_error = driver.find_element(By.TAG_NAME, "h1").text
        if "504" in page_error:
            error_message = f"Carga de página errónea por: {page_error}"
            log_error(error_message)
            close_driver(driver)  # Cierra el navegador si hay un error
            return False
        return True
    except NoSuchElementException:
        return True

def click_documentos_tab(driver):
    """Hace clic en la pestaña de documentos."""
    try:
        documentos_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@data-toggle='tab' and @href='#documentos']"))
        )
        documentos_tab.click()
        log_activity("Clic en la pestaña 'Documentos'.")
    except TimeoutException:
        log_activity("No se pudo hacer clic en la pestaña 'Documentos'.")

def expand_document_section(driver):
    """Expande la sección de Documentos si está colapsada."""
    try:
        # Esperar que el enlace de la sección de documentos sea clicable
        document_section = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='accordion-toggle' and @data-toggle='collapse' and @href='#collapse-documentos']"))
        )
        document_section.click()
        log_activity("Sección 'Documentos' expandida.")
    except TimeoutException:
        log_activity("No se pudo expandir la sección 'Documentos'.")
    except Exception as e:
        log_activity(f"Error inesperado al intentar expandir la sección 'Documentos': {e}")

def process_document_table(driver):
    """Recorre las filas de la tabla y descarga los documentos que correspondan."""
    try:
        # Expande la sección de documentos antes de procesar la tabla
        expand_document_section(driver)

        # Esperar a que la tabla esté presente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'tabla-resultado-busqueda')]/tbody/tr")))
        rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'tabla-resultado-busqueda')]/tbody/tr")

        for row in rows:
            tipo_documento = row.find_element(By.XPATH, ".//td[@data-label='Tipo Documento']").text

            # Condición para buscar y descargar "Informe de Fiscalización Ambiental"
            if "Informe de Fiscalización Ambiental" in tipo_documento and "anexo" not in tipo_documento.lower():
                try:
                    download_link = row.find_element(By.XPATH, ".//td[@data-label='Link']/a")
                    download_url = download_link.get_attribute('href')

                    # Intentar abrir el enlace de descarga
                    driver.get(download_url)
                    log_activity(f"Descargando documento desde: {download_url}")
                    time.sleep(5)  # Ajusta este tiempo según sea necesario

                except NoSuchElementException as e:
                    log_activity(f"Error: No se encontró el enlace de descarga en la fila. Detalle: {e}")
                except Exception as e:
                    log_activity(f"Error al intentar descargar el documento. Detalle: {e}")
            else:
                log_activity(f"Documento ignorado: {tipo_documento}")

    except NoSuchElementException as e:
        log_activity(f"Error al procesar la tabla de documentos: {e}")
    except StaleElementReferenceException:
        log_activity("El elemento ya no es adjunto al DOM. Intentando de nuevo...")
    except TimeoutException:
        log_activity("Tiempo de espera agotado al intentar acceder a la tabla.")

def process_row(driver, row):
    """Procesa una fila de la tabla y descarga el documento correspondiente."""
    wait = WebDriverWait(driver, 10)
    detalle_link = row.find_element(By.XPATH, ".//a[contains(text(),'Ver detalle')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", detalle_link)
    log_activity("Scroll hacia el enlace 'Ver detalle'.")

    detalle_link.click()
    log_activity("Clic en el enlace 'Ver detalle'.")
    wait_for_modal_to_disappear(driver)
    click_documentos_tab(driver)
    process_document_table(driver)
    driver.back()
    log_activity("Volviendo a la página de resultados.")

def select_category(driver):
    """Selecciona la categoría 'Agroindustrias' y hace clic en el botón de buscar."""
    try:
        wait = WebDriverWait(driver, 20)
        category_select = wait.until(EC.presence_of_element_located((By.ID, "categoria")))
        wait.until(EC.element_to_be_clickable((By.ID, "categoria")))
        category_select.click()

        agroindustria_option = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='categoria']/option[@value='6']")))
        agroindustria_option.click()

        log_activity("Categoría 'Agroindustrias' seleccionada.")

        buscar_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Buscar')]")))
        buscar_button.click()
        log_activity("Clic en el botón 'Buscar'.")

    except TimeoutException:
        log_activity("Error al seleccionar la categoría o hacer clic en buscar.")
    except Exception as e:
        log_activity(f"Error inesperado: {e}")

def process_first_category(driver):
    """Realiza la búsqueda en la primera categoría y descarga los documentos fila por fila."""
    base_url = 'https://snifa.sma.gob.cl/Fiscalizacion'
    driver.get(base_url)

    if not check_page_load(driver):
        return

    select_category(driver)
    wait_for_modal_to_disappear(driver)

    wait = WebDriverWait(driver, 10)

    for i in range(1, 30):
        try:
            row_xpath = f"//table/tbody/tr[{i}]"
            row = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
            log_activity(f"Procesando fila {i}...")
            process_row(driver, row)
        except TimeoutException:
            log_activity(f"No se pudo encontrar la fila {i}, terminando proceso.")
            break

def main():
    driver = setup_driver()
    try:
        process_first_category(driver)
    finally:
        close_driver(driver)
        log_activity("Terminando scraping.")

if __name__ == '__main__':
    main()
