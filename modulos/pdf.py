import urllib.request
import io
import PyPDF2
import logging
import os
import shutil

def buscarEnPdf(url):
    try:
        response = urllib.request.urlopen(url, timeout=120)
        pdf_file = io.BytesIO(response.read())
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        palabras_encontradas = []

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            with open('Diccionario.txt', 'r') as dic:
                contenido = dic.read()
                palabras = contenido.split()

            for palabra in palabras:
                if palabra in text:
                    palabras_encontradas.append(palabra)

        return palabras_encontradas

    except (urllib.request.HTTPError, urllib.request.URLError) as e:
        logging.info(f"Error al descargar el archivo PDF: {e}")

def analizar_pdf(nombre_archivo):
    try:
        resultados = []
        with open(nombre_archivo, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                with open('Diccionario.txt', 'r') as dic:
                    contenido = dic.read()
                    palabras = contenido.split()
                for palabra in palabras:
                    if palabra in text:
                        resultados.append(palabra)
        return resultados
    except Exception as e:
        logging.info(f"Error al analizar el archivo PDF: {e}")
        return []

def eliminar_archivos_carpeta(carpeta):
    for nombre_archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, nombre_archivo)
        try:
            if os.path.isfile(ruta_archivo) or os.path.islink(ruta_archivo):
                os.unlink(ruta_archivo)
            elif os.path.isdir(ruta_archivo):
                shutil.rmtree(ruta_archivo)
        except Exception as e:
            logging.info(f"Error al eliminar {ruta_archivo}. Razón: {e}")
