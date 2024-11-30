import os
from PyPDF2 import PdfReader 
import docx2txt
import re
import logging

diccionario = ["olor", "olores"]

ruta_descargas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Descargas')


def mostrar_contenido_archivo():
    #logging.info("Iniciando analisis")
    print(f"Ruta de descargas: {ruta_descargas}")
    #logging.info(f"Ruta de descargas: {ruta_descargas}")
    
    try:
        archivos = os.listdir(ruta_descargas)
        print(f"Archivos encontrados: {archivos}")
        #logging.info(f"Archivos encontrados: {archivos}")
    except FileNotFoundError:
        print(f"No se encontró el directorio: {ruta_descargas}")
        return
    except PermissionError:
        print(f"Permiso denegado para acceder al directorio: {ruta_descargas}")
        return

    resultados = []

    for archivo in archivos:
        ruta_archivo = os.path.join(ruta_descargas, archivo)
        
        try:
            if archivo.lower().endswith('.docx'):
                texto = docx2txt.process(ruta_archivo)
                for palabra in diccionario:
                    coincidencias = re.findall(rf'\b{palabra}\b', texto, re.IGNORECASE)
                    if coincidencias:
                        resultados.append([len(coincidencias), palabra])
                        print(f"'{palabra}' se encontró {len(coincidencias)} veces en {archivo}")
            elif archivo.lower().endswith('.pdf'):
                with open(ruta_archivo, 'rb') as file:
                    lector_pdf = PdfReader(file)
                    for pagina in range(len(lector_pdf.pages)):
                        pagina_obj = lector_pdf.pages[pagina]
                        texto = pagina_obj.extract_text()
                        for palabra in diccionario:
                            coincidencias = re.findall(rf'\b{palabra}\b', texto, re.IGNORECASE)
                            if coincidencias:
                                resultados.append([len(coincidencias), palabra])
                                print(f"'{palabra}' se encontró {len(coincidencias)} veces en {archivo} (página {pagina + 1})")
            else:
                print(f"Archivo {archivo} no es un .docx o .pdf")
        except Exception as e:
            print(f"Error al procesar el archivo {archivo}: {e}")
            raise  # Vuelve a lanzar la excepción para ver el error completo
    return resultados


def eliminar_contenido_directorio(ruta_descargas):
    """Elimina todos los archivos en el directorio especificado, excepto '.gitkeep'."""
    try:
        for archivo in os.listdir(ruta_descargas):
            if archivo == ".gitkeep":
                continue
            ruta_archivo = os.path.join(ruta_descargas, archivo)
            try:
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
                    print(f"Archivo {archivo} eliminado.")
                    logging.info(f"Archivo {archivo} eliminado.")
                elif os.path.isdir(ruta_archivo):
                    os.rmdir(ruta_archivo)
                    print(f"Directorio {archivo} eliminado.")
                    logging.info(f"Directorio {archivo} eliminado.")
            except Exception as e:
                print(f"Error al eliminar {archivo}: {e}")
                logging.info(f"Error al eliminar {archivo}: {e}")
    except Exception as e:
        print(f"Error al acceder al directorio {ruta_descargas}: {e}")
        logging.info(f"Error al acceder al directorio {ruta_descargas}: {e}")

# mostrar_contenido_archivo()
