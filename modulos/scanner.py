import os
import django
from django.conf import settings
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from odorwatch.models import Palabras

def obtener_palabras():
    """Obtiene todas las palabras del modelo Palabras."""
    try:
        palabras = Palabras.objects.all()
        lista_palabras = [palabra.palabra for palabra in palabras]
        return lista_palabras
    except Exception as e:
        print(f"Error al obtener palabras: {e}")
        return []

from odorwatch.models import Coincidencias, Documento

def contar_coincidencias(documento, palabras_buscadas, nombre_documento):
    """
    Cuenta cuántas veces se encuentran las palabras buscadas en el documento y guarda el nombre del documento en el modelo Coincidencias.
    
    Args:
        documento (str): El contenido del documento en el que se buscarán las palabras.
        palabras_buscadas (list): Lista de palabras a buscar en el documento.
        nombre_documento (str): El nombre del documento.
    
    Returns:
        dict: Un diccionario con las palabras como claves y el número de coincidencias como valores.
    """
    conteo_coincidencias = {palabra: 0 for palabra in palabras_buscadas}
    
    # Contar las coincidencias de cada palabra en el documento
    for palabra in palabras_buscadas:
        conteo_coincidencias[palabra] = documento.lower().count(palabra.lower())
        logging.info(f"Palabra '{palabra}' encontrada {conteo_coincidencias[palabra]} veces en el documento '{nombre_documento}'.")

    # Obtener el objeto Documento relacionado
    try:
        documento_obj = Documento.objects.get(nombre=nombre_documento)
    except Documento.DoesNotExist:
        logging.info(f"Documento '{nombre_documento}' no encontrado en la base de datos.")
        return conteo_coincidencias

    # Guardar el nombre del documento y las coincidencias en el modelo Coincidencias
    for palabra, conteo in conteo_coincidencias.items():
        if conteo > 0:
            try:
                Coincidencias.objects.create(
                    documento=documento_obj,
                    palabra=palabra,
                    conteo=conteo
                )
                logging.info(f"Coincidencia guardada: {palabra} - {conteo} veces en '{nombre_documento}'.")
            except Exception as e:
                logging.info(f"Error al guardar la coincidencia en la base de datos: {e}")
    
    return conteo_coincidencias


# Ejemplo de uso
if __name__ == "__main__":
    palabras = obtener_palabras()
    print("Palabras obtenidas:", palabras)
