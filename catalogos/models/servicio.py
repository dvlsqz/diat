from django.db import models


class Servicio(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', unique=True)

    class Meta:
        app_label = 'catalogos'
        verbose_name = 'servicio'
        verbose_name_plural = 'servicios'

    def __str__(self):
        return self.nombre
