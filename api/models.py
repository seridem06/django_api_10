from django.db import models

class EsquemaNegocio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    config = models.JSONField(default=dict) # Guarda idAutomatico
    campos = models.JSONField() # Guarda la lista de campos definidos

    def __str__(self):
        return self.nombre

class DatoNegocio(models.Model):
    negocio = models.CharField(max_length=100) # Nombre del negocio al que pertenece
    contenido = models.JSONField() # Guarda el registro completo (DNI, Fecha, etc.)

    def __str__(self):
        return f"{self.negocio} - ID {self.contenido.get('id')}"