import logging
from django.shortcuts import render
from odorwatch.models import Cliente, UnidadFiscalizable, Documento, Coincidencias, Palabras

# Enviar datos a Cliente 
def add_cliente(nombre_cliente):
    """Añade un nuevo cliente a la base de datos."""
    logging.info("Añadiendo Cliente a BD")
    try:
        if not nombre_cliente:
            return "El nombre del cliente es requerido."

        # Crea o obtiene el cliente en la base de datos
        cliente, created = Cliente.objects.get_or_create(nombre=nombre_cliente)

        if created:
            logging.info("2- El usuario ha sido recibido")
            return f"Cliente '{nombre_cliente}' añadido a la base de datos."
        else:
            return f"Cliente '{nombre_cliente}' ya existe en la base de datos."

    except Exception as e:
        return f"Error al añadir el cliente: {str(e)}"

# Enviar datos a Unidad Fiscalizable
def add_unidad(nombre_unidad, ubicacion_unidad, url_unidad, nombre_cliente):
    """Añade una nueva unidad fiscalizable a la base de datos."""
    logging.info("Añadiendo Unidad Fiscalizable a BD")
    try:
        if not nombre_unidad or not nombre_cliente or not ubicacion_unidad or not url_unidad:
            return "Los datos son requeridos."

        # Obtiene el cliente de la base de datos
        cliente = Cliente.objects.get(nombre=nombre_cliente)

        # Crea o obtiene la unidad fiscalizable en la base de datos
        ufiscal, created = UnidadFiscalizable.objects.get_or_create(
            nombre=nombre_unidad,
            ubicacion=ubicacion_unidad,
            url=url_unidad,
            cliente=cliente
        )

        if created:
            logging.info("2- La unidad fiscalizable ha sido añadida")
            return f"Unidad Fiscalizable '{nombre_unidad}' añadida a la base de datos."
        else:
            return f"Unidad Fiscalizable '{nombre_unidad}' ya existe en la base de datos."

    except Cliente.DoesNotExist:
        return f"Error: Cliente '{nombre_cliente}' no encontrado."
    except Exception as e:
        return f"Error al añadir la unidad fiscalizable: {str(e)}"

# Enviar datos a Unidad Fiscalizable
def add_documento(url, unidad_fiscalizable, nombre_documento):
    """Añade un nuevo documento a la base de datos."""
    logging.info("--------------------------")
    logging.info("Añadiendo Documento a BD")
    logging.info(url)
    logging.info(unidad_fiscalizable)
    logging.info(nombre_documento)
    logging.info("--------------------------")
    try:
        if not unidad_fiscalizable or not url or not nombre_documento:
            return "Los datos son requeridos."

        # Obtiene la unidad fiscalizable de la base de datos
        ufiscalizable = UnidadFiscalizable.objects.get(nombre=unidad_fiscalizable)

        # Crea o obtiene el documento en la base de datos
        doc, created = Documento.objects.get_or_create(
            nombre_documento=nombre_documento,
            url=url,
            unidad_fiscalizable=ufiscalizable
        )

        if created:
            logging.info("El documento ha sido añadido a la BD")
            return f"Documento '{nombre_documento}' añadido a la base de datos."
        else:
            return f"Documento '{nombre_documento}' ya existe en la base de datos."

    except UnidadFiscalizable.DoesNotExist:
        return f"Error: Unidad Fiscalizable '{unidad_fiscalizable}' no encontrada."
    except Exception as e:
        return f"Error al añadir documento: {str(e)}"


def add_coincidencias(cantidad, url_documento, palabras):
    logging.info("--------------------------")
    logging.info("Añadiendo Coincidencias a BD")
    logging.info(f"Cantidad: {cantidad}, URL: {url_documento}, Palabras: {palabras}")
    logging.info("--------------------------")
    try:
        if not cantidad or not url_documento or not palabras:
            return "Los datos son requeridos."

        # Obtiene el documento de la base de datos
        documento = Documento.objects.get(url=url_documento)

        # Obtiene las palabras de la base de datos
        palabras_obj, created = Palabras.objects.get_or_create(palabras=palabras)

        # Crea o obtiene la coincidencia en la base de datos
        coincidencia, created = Coincidencias.objects.get_or_create(
            cantidad=cantidad,
            documento=documento,
            palabras=palabras_obj
        )

        if created:
            logging.info("La coincidencia ha sido añadida a la BD")
            return f"Coincidencia añadida a la base de datos."
        else:
            return f"Coincidencia ya existe en la base de datos."

    except Documento.DoesNotExist:
        return f"Error: Documento '{url_documento}' no encontrado."
    except Palabras.DoesNotExist:
        return f"Error: Palabras '{palabras}' no encontradas."
    except Exception as e:
        logging.error(f"Error al añadir coincidencia: {str(e)}")
        return f"Error al añadir coincidencia: {str(e)}"
