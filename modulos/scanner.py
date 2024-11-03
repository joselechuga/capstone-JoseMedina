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

# Ejemplo de uso
if __name__ == "__main__":
    palabras = obtener_palabras()
    print("Palabras obtenidas:", palabras)
