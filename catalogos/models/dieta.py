from django.db import models


class Dieta(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    npo = models.BooleanField(default=False,  verbose_name='Dieta para pacientes NPO')
    viaje = models.BooleanField(default=False, verbose_name='Dieta de viaje')

    class Meta:
        app_label = 'catalogos'
        verbose_name = 'dieta'
        verbose_name_plural = 'dietas'

    def __str__(self):
        return self.nombre

    def as_json_basico(self):
        return {'id': str(self.id), 'text': self.nombre, 'nombre': self.nombre, 'npo': self.npo, 'viaje': self.viaje}
