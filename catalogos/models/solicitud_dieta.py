from django.contrib.auth.models import User
from django.db import models

from catalogos.models.dieta import Dieta
from django_extensions.db.models import TimeStampedModel

from catalogos.models.jornada import Jornada
from catalogos.models.servicio import Servicio


class SolicitudDieta(TimeStampedModel):
    servida = models.BooleanField(default=False, verbose_name='Dieta Servida')
    total_dietas_servidas = models.PositiveIntegerField(default=0, verbose_name='Total de dietas Servidas')

    # Relaciones
    servicio = models.ForeignKey(Servicio, verbose_name='Servicio', related_name='dieta_servicio',
                                 on_delete=models.PROTECT)

    jornada = models.ForeignKey(Jornada, verbose_name='Jornada', related_name='dieta_jornada', on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, verbose_name='Usuario Registro', related_name='dieta_usuario_registro',
                                on_delete=models.PROTECT)
    usuario_sirvio = models.ForeignKey(User, verbose_name='Usuario Sirvio', related_name='dieta_usuario_sirvio',
                                       on_delete=models.PROTECT)

    class Meta:
        app_label = 'catalogos'
        verbose_name = 'solicitud_dieta'
        verbose_name_plural = 'solicitudes_de_dieta'

    def __str__(self):
        return self.id


class DetalleSolicitudDieta(models.Model):
    no_cama = models.CharField(verbose_name='No. de cama', max_length=20, null=True, blank=True)
    especificar = models.CharField(max_length=200, verbose_name='Especificar', null=True, blank=True)

    # Relaciones
    solicitud_dieta = models.ForeignKey(SolicitudDieta, verbose_name='Solicitud de Dieta No.',
                                        related_name='detalle_solicitud', on_delete=models.PROTECT)
    dieta = models.ForeignKey(Dieta, verbose_name='Dieta', related_name='detalle_dieta', on_delete=models.PROTECT)

    class Meta:
        app_label = 'catalogos'
        verbose_name = 'detalle_solicitud'
        verbose_name_plural = 'detalles_solicitud'

    def __str__(self):
        return self.id


class SolicitudDietaTiempoEstablecido(models.Model):
    no_dietas_a_solicitar = models.PositiveIntegerField(verbose_name="No. de solicitudes de dietas")
    inicio = models.DateTimeField("Inicio")
    fin = models.DateTimeField("Fin")
    usuario = models.ForeignKey(User, verbose_name='Usuario', related_name='solicitud_dieta_tiempo_usuario',
                                on_delete=models.PROTECT)

    class Meta:
        app_label = 'catalogos'
        verbose_name = 'solicitud_dieta_tiempo_establecido'
        verbose_name_plural = 'solicitudes_dietas_tiempo_establecido'

    def __str__(self):
        return str(self.id)
