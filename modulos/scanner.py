import os
from PyPDF2 import PdfReader
from django.conf import settings
from modulos.models import Palabras, Coincidencias, Documento

def scan_pdfs_and_record_coincidences():
    """Escanea archivos PDF en la carpeta Descargas y registra coincidencias en la base de datos."""
    download_dir = os.path.join(settings.BASE_DIR, 'modulos', 'Descargas')
    palabras = Palabras.objects.all()

    for filename in os.listdir(download_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(download_dir, filename)
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()

                for palabra in palabras:
                    count = text.lower().count(palabra.palabras.lower())
                    if count > 0:
                        # Asumiendo que tienes un documento relacionado con el archivo PDF
                        documento = Documento.objects.filter(url=file_path).first()
                        if documento:
                            Coincidencias.objects.create(
                                cantidad=count,
                                documento=documento,
                                palabras=palabra
                            )
                            print(f"Coincidencias encontradas: {count} para la palabra '{palabra.palabras}' en el documento '{filename}'")
