from django.db import models


class Jornada(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Fin')

    class Meta:
        app_label = 'catalogos'
        verbose_name = 'jornada'
        verbose_name_plural = 'jornadas'

    def __str__(self):
        return '%s %s %s' % (self.nombre, self.hora_inicio, self.hora_fin)
