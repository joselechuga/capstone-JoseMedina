from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Palabras(models.Model):
    palabras = models.CharField(max_length=150)

    def __str__(self):
        return self.palabras


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    rol = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class UnidadFiscalizable(models.Model):
    nombre = models.CharField(max_length=150)
    ubicacion = models.CharField(max_length=150)
    url = models.URLField(max_length=255)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="unidades_fiscalizables")

    def __str__(self):
        return self.nombre


class Documento(models.Model):
    url = models.URLField(max_length=255)
    unidad_fiscalizable = models.ForeignKey(UnidadFiscalizable, on_delete=models.CASCADE, related_name="documentos")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="documentos")

    def __str__(self):
        return f"Documento de {self.unidad_fiscalizable.nombre}"


class Coincidencias(models.Model):
    cantidad = models.IntegerField()
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name="coincidencias")
    palabras = models.ForeignKey(Palabras, on_delete=models.CASCADE, related_name="coincidencias")

    def __str__(self):
        return f"Coincidencias en {self.documento} - {self.cantidad}"


class LogsUsuario(models.Model):
    accion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="logs")

    def __str__(self):
        return f"Log de {self.usuario} - {self.fecha_hora}"
