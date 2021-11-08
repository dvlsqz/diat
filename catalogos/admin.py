from django.contrib import admin

from catalogos.models import Dieta, Jornada, Servicio, SolicitudDietaTiempoEstablecido


class DietaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'npo', 'viaje')


class JornadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'hora_inicio', 'hora_fin')


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class SolicitudDietaAdmin(admin.ModelAdmin):
    list_display = ('id', )


class SolicitudDietaTiempoEstablecidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'no_dietas_a_solicitar', 'inicio', 'fin', 'usuario')


admin.site.register(Dieta, DietaAdmin)
admin.site.register(Jornada, JornadaAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(SolicitudDietaTiempoEstablecido, SolicitudDietaTiempoEstablecidoAdmin)
