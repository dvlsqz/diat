from django import template
from django.utils import timezone

from catalogos.models import SolicitudDietaTiempoEstablecido

register = template.Library()


@register.filter(name='solicitudes_disponibles')
def solicitudes_disponibles(user):
    disponibles = SolicitudDietaTiempoEstablecido.objects.filter(usuario=user)
    if disponibles.count() > 0:
        fecha_hora = timezone.now().astimezone(tz=timezone.utc)
        item = disponibles.last()
        inicio = item.inicio.astimezone(tz=timezone.utc)
        fin = item.fin.astimezone(tz=timezone.utc)
        if inicio < fecha_hora < fin:
            return item.no_dietas_a_solicitar > 0
    return False
