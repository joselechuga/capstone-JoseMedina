import PyPDF2
import os
import docx
from odorwatch.models import Palabras
from main import log_activity

def procesar_documentos(directorio):
    contenido = ""
    archivos = os.listdir(directorio)
    print("Archivos en el directorio:", archivos)  # Imprime los archivos disponibles
    for nombre_archivo in archivos:
        if nombre_archivo == '.gitkeep':
            continue
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        if nombre_archivo.endswith('.pdf'):
            with open(ruta_archivo, 'rb') as archivo_pdf:
                lector_pdf = PyPDF2.PdfReader(archivo_pdf)
                for pagina in lector_pdf.pages:
                    contenido += pagina.extract_text() or ""
        elif nombre_archivo.endswith('.docx'):
            try:
                documento = docx.Document(ruta_archivo)
                for parrafo in documento.paragraphs:
                    contenido += parrafo.text or ""
            except Exception as e:
                print(f"Error al procesar el archivo {nombre_archivo}: {e}")
    return contenido

def buscar_palabras(contenido, nombre_archivo):
    if nombre_archivo == '.gitkeep':
        return {}  # Ignorar el archivo .gitkeep
    resultados = {}
    palabras = Palabras.objects.all().values_list('palabras', flat=True)
    for palabra in palabras:
        if palabra in contenido:
            resultados[palabra] = True
            print('**********************************************************************')
            print(f"La palabra '{palabra}' se encontró en el documento '{nombre_archivo}'.")
            print('**********************************************************************')
        else:
            resultados[palabra] = False
            print(f"La palabra '{palabra}' no se encontró en el documento '{nombre_archivo}'.")
    return resultados

def eliminar_archivos_sin_palabras(directorio, palabras):
    archivos = os.listdir(directorio)
    for nombre_archivo in archivos:
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        if nombre_archivo.endswith('.pdf') or nombre_archivo.endswith('.docx'):
            contenido = ""
            if nombre_archivo.endswith('.pdf'):
                with open(ruta_archivo, 'rb') as archivo_pdf:
                    lector_pdf = PyPDF2.PdfReader(archivo_pdf)
                    for pagina in lector_pdf.pages:
                        contenido += pagina.extract_text() or ""
            elif nombre_archivo.endswith('.docx'):
                try:
                    documento = docx.Document(ruta_archivo)
                    for parrafo in documento.paragraphs:
                        contenido += parrafo.text or ""
                except Exception as e:
                    print(f"Error al procesar el archivo {nombre_archivo}: {e}")
                    continue

            contiene_palabras = any(palabra in contenido for palabra in palabras)
            if not contiene_palabras:
                os.remove(ruta_archivo)
                print(f"El archivo '{nombre_archivo}' ha sido eliminado porque no contiene las palabras buscadas.")


def main():
    try:
        directorio = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Descargas')
        contenido = procesar_documentos(directorio)
        palabras_buscadas = Palabras.objects.all().values_list('palabras', flat=True)
        
        # Buscar palabras en cada archivo
        for nombre_archivo in os.listdir(directorio):
            buscar_palabras(contenido, nombre_archivo)
        
        # Eliminar archivos que no contienen las palabras buscadas
        eliminar_archivos_sin_palabras(directorio, palabras_buscadas)
        
    except FileNotFoundError:
        print("Error: El archivo no se encontró.")
    except Exception as e:
        print(f"Se produjo un error: {e}")

if __name__ == "__main__":
    main()