from django.urls import path

from . import views

app_name = 'catalogos'
urlpatterns = [
    # Urls de usuarios
    path('users/', views.UsersListView.as_view(), name='users'),
    path('users/users-json/', views.UsersListJson.as_view(), name='users-json'),
    path('users/user-create/', views.UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/user-update/', views.UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/user-delete/', views.UserDeleteJsonView.as_view(), name='user-delete'),
    path('users/<int:pk>/user-details/', views.UserDetailsView.as_view(), name='user-details'),

    # Urls de servicios
    path('servicios/', views.ServiciosListView.as_view(), name='servicios'),
    path('servicios/articulos-json/', views.ServiciosListJson.as_view(), name='servicios-json'),
    path('servicios/articulo-create/', views.ServicioCreateView.as_view(), name='servicio-create'),
    path('servicios/<int:pk>/articulo-update/', views.ServicioUpdateView.as_view(), name='servicio-update'),
    path('servicios/<int:pk>/articulo-delete/', views.ServicioDeleteJsonView.as_view(), name='servicio-delete'),

    # Urls de jornadas
    path('jornadas/', views.JornadasListView.as_view(), name='jornadas'),
    path('jornadas/jornadas-json/', views.JornadasListJson.as_view(), name='jornadas-json'),
    path('jornadas/jornada-create/', views.JornadaCreateView.as_view(), name='jornada-create'),
    path('jornadas/<int:pk>/jornada-update/', views.JornadaUpdateView.as_view(),
         name='jornada-update'),
    path('jornadas/<int:pk>/jornada-delete/', views.JornadaDeleteJsonView.as_view(),
         name='jornada-delete'),

    # Urls de dietas
    path('dietas/', views.DietasListView.as_view(), name='dietas'),
    path('dietas/dietas-json/', views.DietasListJson.as_view(), name='dietas-json'),
    path('dietas/dietas-json/<int:json>', views.DietasListJson.as_view(), name='dietas-json'),
    path('dietas/dieta-create/', views.DietaCreateView.as_view(), name='dieta-create'),
    path('dietas/<int:pk>/dieta-update/', views.DietaUpdateView.as_view(), name='dieta-update'),
    path('dietas/<int:pk>/dieta-delete/', views.DietaDeleteJsonView.as_view(), name='dieta-delete'),
    path('dietas/<int:pk>/dieta-get/', views.DietaGetView.as_view(), name='dieta-get'),

    # Urls de solicitudes de dietas
    path('solicitudes-dietas/', views.SolicitudesDietaListView.as_view(), name='solicitudes-dietas'),
    path('solicitudes-dietas/servidas/', views.SolicitudesDietasServidasListView.as_view(),
         name='solicitudes-dietas-servidas'),
    path('solicitudes-dietas/encargados/', views.SolicitudesDietasEncargadoListView.as_view(),
         name='solicitudes-dietas-encargado'),
    path('solicitudes-dietas/<int:solicitudes>/solicitudes-dietas-json/', views.SolicitudesDietasListJson.as_view(),
         name='solicitudes-dietas-json'),
    path('solicitudes-dietas/solicitud-dieta-create/', views.SolicitudDietaCreateView.as_view(),
         name='solicitud-dieta-create'),
    path('solicitudes-dietas/<int:pk>/solicitud-dieta-details/', views.SolicitudDietaDetailsView.as_view(),
         name='solicitud-dieta-details'),
    path('solicitudes-dietas/<int:pk>/solicitud-dieta-aprobar/', views.SolicitudDietaServidaJsonView.as_view(),
         name='solicitud-dieta-servida'),
    path('solicitudes-dietas/<int:pk>/solicitud-dieta-delete/', views.SolicitudDietaDeleteJsonView.as_view(),
         name='solicitud-dieta-delete'),
    path('solicitudes-dietas/<int:pk>/solicitud-dieta-total/', views.SolicitudDietaTotalDietasJsonView.as_view(),
         name='solicitud-dieta-total-solicitudes'), 
    path('solicitudes-dietas/<int:pk>/pdf/', views.SolicitudDietaExcelView.as_view(), name='solicitud-dieta-excel'),

    # Urls de detalles de solicitud de dietas
    path('solicitudes-dietas/detalle-solicitud-dieta-create/', views.DetalleSolicitudDietaCreateView.as_view(),
         name='detalle-solicitud-dieta-create'),

    # Urls de informes
    path('informes/totales-solicitudes-diarias', views.SolicitudesDiariasJsonView.as_view(),
         name='totales-solicitudes-diarias'),
    path('informes/tipos-informes', views.SolicitudesDietasInformesJsonView.as_view(),
         name='tipos-informes'),
    path('informes/tipos-informes/pdf/', views.SDInformesRangeJsonView.as_view(), name='sd-fechas-pdf'),
    path('informes/matriz', views.MatrizView.as_view(), name='matriz'),
    path('informes/matriz/excel/', views.MatrizExportView.as_view(), name='matriz-excel'),
    path('informes/estado-dietas/pdf/', views.EstadoDietasPdfView.as_view(), name='estado-dietas-pdf'),
    path('informes/jorandas/pdf/', views.SolicitudesJornadaPdfView.as_view(), name='jornadas-pdf'),
    path('informes/dietas/pdf/', views.SolicitudesDietaPdfView.as_view(), name='dietas-pdf'),
    path('informes/servicios/pdf/', views.SolicitudesServiciosPdfView.as_view(), name='servicios-pdf'),
    path('informes/estado-dietas-range/pdf/', views.EstadoDietasRangePdfView.as_view(), name='estado-dietas-range-pdf'),
    path('informes/jornadas-range/pdf/', views.SolicitudesJornadaRangePdfView.as_view(), name='jornadas-range-pdf'),

    # Urls para solicitudes de dietas en un tiempo establecido
    path('solicitudes-dietas/<int:user_id>/tiempo-establecido',
         views.SolicitudDietasTiempoEstablecidoListView.as_view(), name='list-tiempo-establecido-user'),
    path('solicitudes-dietas/<int:user_id>/solicitudes-te-json/', views.SolicitudDietasTiempoEstablecidoListJson.as_view(),
         name='solicitudes-dietas-tiempo-establecido-json'),
    path('solicitudes-dietas/<int:user_id>/solicitudes-te-create/',
         views.SolicitudDietasTiempoEstablecidoCreateView.as_view(), name='sd-te-create'),
    path('solicitudes-dietas/solicitudes-te-create/',
         views.SolicitudDietasTiempoEstablecidoCreateView.as_view(), name='sd-te-create2'),
    path('solicitudes-dietas/solicitudes-te-create-solicitud/',
         views.SolicitudDietaTiempoEstablecidoCreateSolicitudView.as_view(), name='solicitud-dieta-te-create'),
]