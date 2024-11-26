import os
from docx import Document
import PyPDF2

def mostrar_contenido_archivo():
    ruta_descargas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Descargas')
    print(f"Ruta de descargas: {ruta_descargas}")
    
    try:
        archivos = os.listdir(ruta_descargas)
        print(f"Archivos encontrados: {archivos}")
    except FileNotFoundError:
        print(f"No se encontró el directorio: {ruta_descargas}")
        return
    except PermissionError:
        print(f"Permiso denegado para acceder al directorio: {ruta_descargas}")
        return

    for archivo in archivos:
        ruta_archivo = os.path.join(ruta_descargas, archivo)
        
        try:
            if archivo.endswith('.docx'):
                doc = Document(ruta_archivo)
                for para in doc.paragraphs:
                    if "olor" in para.text or "olores" in para.text:
                        print(para.text)
            elif archivo.endswith('.pdf'):
                with open(ruta_archivo, 'rb') as file:
                    lector_pdf = PyPDF2.PdfReader(file)
                    for pagina in range(len(lector_pdf.pages)):
                        pagina_obj = lector_pdf.pages[pagina]
                        texto = pagina_obj.extract_text()
                        if "olor" in texto or "olores" in texto:
                            print(texto)
            else:
                print(f"Archivo {archivo} no es un .docx o .pdf")
        except Exception as e:
            print(f"Error al procesar el archivo {archivo}: {e}")
            raise  # Vuelve a lanzar la excepción para ver el error completo
