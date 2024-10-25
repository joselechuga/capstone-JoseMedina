from django.db import models

# Create your models here.
class Cliente(models.Model):
    id = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 100, unique=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app'
    
class Estado(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length = 150)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app'
        
class Unidad_fiscalizable(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length = 150)
    expediente = models.CharField(max_length=150)
    url = models.CharField(max_length=255)    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado,on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app'
    


class Tipo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length = 150)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        app_label = 'app'

class Documento(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(verbose_name='Link Unidad Fiscalizable',max_length=255) 
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
    unidad_fiscalizable = models.ForeignKey(Unidad_fiscalizable, on_delete=models.CASCADE)
    
    def __str__(self):
            return f"{str(self.tipo)} > {str(self.unidad_fiscalizable)}"
    
    class Meta:
        app_label = 'app'

class Palabras(models.Model):
    id = models.AutoField(primary_key=True)
    palabras = models.CharField(max_length = 150, default='Vacio')
    
    def __str__(self):
        return self.palabras
    
    class Meta:
        app_label = 'app'

class Coincidencias(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad = models.IntegerField(default=0)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    palabras = models.ForeignKey(Palabras, on_delete=models.CASCADE)
    
    
    def __str__(self):
        return f"{str(self.palabras)} : {str(self.cantidad)} {str(self.documento)}"
    
    class Meta:
        app_label = 'app'
    
