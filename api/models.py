from django.db import models

class EsquemaNegocio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    config = models.JSONField(default=dict)  # Guarda idAutomatico
    campos = models.JSONField()  # Guarda la lista de campos definidos

    class Meta:
        verbose_name = "Esquema de Negocio"
        verbose_name_plural = "Esquemas de Negocios"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DatoNegocio(models.Model):
    negocio = models.CharField(max_length=100)  # Nombre del negocio al que pertenece
    contenido = models.JSONField()  # Guarda el registro completo (DNI, Fecha, etc.)
    
    # Campos automáticos de auditoría (opcional pero recomendado)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Dato de Negocio"
        verbose_name_plural = "Datos de Negocios"
        ordering = ['negocio', '-id']
        indexes = [
            models.Index(fields=['negocio']),  # Índice para búsquedas rápidas
        ]

    def __str__(self):
        return f"{self.negocio} - ID {self.contenido.get('id', 'Sin ID')}"