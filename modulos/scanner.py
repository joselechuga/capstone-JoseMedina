import os
import django
from django.conf import settings

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

def contar_coincidencias(documento, palabras_buscadas):
    """
    Cuenta cuántas veces se encuentran las palabras buscadas en el documento.
    
    Args:
        documento (str): El contenido del documento en el que se buscarán las palabras.
        palabras_buscadas (list): Lista de palabras a buscar en el documento.
    
    Returns:
        dict: Un diccionario con las palabras como claves y el número de coincidencias como valores.
    """
    conteo_coincidencias = {palabra: 0 for palabra in palabras_buscadas}
    
    for palabra in palabras_buscadas:
        conteo_coincidencias[palabra] = documento.lower().count(palabra.lower())
    
    return conteo_coincidencias


# Ejemplo de uso
if __name__ == "__main__":
    palabras = obtener_palabras()
    print("Palabras obtenidas:", palabras)
