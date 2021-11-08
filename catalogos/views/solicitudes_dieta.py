from datetime import datetime

from django.db import transaction
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import activate, localtime, now

from nutricion_igss import settings

activate(settings.TIME_ZONE)

from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django_datatables_view.base_datatable_view import BaseDatatableView
from catalogos.forms import SolicitudDietaForm
from catalogos.forms.solicitud_dieta import DetalleSolicitudDietaForm
from catalogos.models import SolicitudDieta, Dieta, DetalleSolicitudDieta, Jornada
from utils.PermissionsMixim import GroupRequiredMixin
from utils.ResponseMixim import CreateFormResponseMixin, JsonDeleteView

from utils.SolicitudDietaExport import SolicitudDietaExcel

import os
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa

class SolicitudesDietaListView(GroupRequiredMixin, TemplateView):
    group_required = ['Administrador']
    template_name = 'solicitudes_dietas/list-solicitudes.html'


class SolicitudesDietasServidasListView(GroupRequiredMixin, TemplateView):
    group_required = ['Administrador']
    template_name = 'solicitudes_dietas/list-servidas.html'


class SolicitudesDietasEncargadoListView(GroupRequiredMixin, TemplateView):
    group_required = ['Encargado']
    template_name = 'solicitudes_dietas/list-solicitudes-encargado.html'


class SolicitudesDietasListJson(BaseDatatableView):
    model = SolicitudDieta
    columns = ['id', 'created', 'jornada.nombre', 'servicio.nombre', 'usuario.username', 'usuario_sirvio.username',
               'total_dietas_servidas']
    order_columns = ['id', 'created', 'jornada.nombre', 'servicio.nombre', 'usuario.username',
                     'usuario_sirvio.username', 'total_dietas_servidas']

    def get_initial_queryset(self):
        if self.kwargs.get('solicitudes') == 1:
            return SolicitudDieta.objects.filter(servida=False)
        if self.kwargs.get('solicitudes') == 2:
            # Filtrar solo las soliciutdes diarias de un encargado
            now_begin = datetime.now().replace(hour=0, minute=00)
            now_end = datetime.now().replace(hour=23, minute=59)
            dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
            return dietas_diarias.filter(servida=False, usuario_id=self.request.user.pk)
        return SolicitudDieta.objects.filter(servida=True)


class SolicitudDietaDetailsView(GroupRequiredMixin, DetailView):
    group_required = ['Administrador', 'Encargado']
    model = SolicitudDieta
    template_name = 'solicitudes_dietas/details.html'

    def get_context_data(self, **kwargs):
        context = super(SolicitudDietaDetailsView, self).get_context_data(**kwargs)
        detalles = []

        dietas_distintas = DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=self.object.pk)\
            .values('dieta_id').distinct()

        total_dietas_solicitadas = 0
        for dieta in dietas_distintas:
            data = DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=self.object.pk,
                                                        dieta_id=dieta.get('dieta_id'))
            detalle = {
                'dieta_nombre': data.first().dieta.nombre,
                'camas': data.values('no_cama'),
                'descripciones': data.values('especificar'),
                'total': data.exclude(dieta__npo=True).count(),
            }
            detalles.append(detalle)
            total_dietas_solicitadas += data.exclude(dieta__npo=True).count()

        context['detalles'] = detalles
        context['total_dietas_solicitadas'] = total_dietas_solicitadas
        return context


class SolicitudDietaCreateView(GroupRequiredMixin, CreateView, CreateFormResponseMixin):
    group_required = ['Administrador', 'Encargado']
    template_name = 'solicitudes_dietas/create.html'
    model = SolicitudDieta
    form_class = SolicitudDietaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dietas'] = Dieta.objects.all()
        detalles_formset = formset_factory(DetalleSolicitudDietaForm, extra=0)
        context['formsetDetalles'] = detalles_formset(prefix='Detalles')
        return context

    def form_valid(self, form):
        errores = []
        detalles_formset = formset_factory(DetalleSolicitudDietaForm)
        formset_detalles = detalles_formset(self.request.POST, self.request.FILES, prefix='Detalles')

        if int(self.request.POST.get('Detalles-TOTAL_FORMS', 0)) == 0:
            errores.append('No se han ingresado dietas a la solicitud.')

        jornada = Jornada.objects.get(pk=self.request.POST.get('jornada'))
        time = localtime(now()).time()
        user_groups = []
        for group in self.request.user.groups.values_list('name', flat=True):
            user_groups.append(group)
        group_adm = len(set(user_groups).intersection(["Administrador"]))

        if jornada.hora_inicio < time < jornada.hora_fin or group_adm > 0:
            with transaction.atomic():
                solicitud_dieta = form.save(commit=False)
                solicitud_dieta.usuario_id = self.request.user.id
                solicitud_dieta.usuario_sirvio_id = self.request.user.id
                solicitud_dieta.save()
                if formset_detalles.is_valid():
                    # Guardar Listado de almacenes
                    for item in formset_detalles:
                        detalle = item.save(commit=False)
                        detalle.solicitud_dieta_id = solicitud_dieta.pk
                        detalle.save()
            return JsonResponse({'result': 'OK', 'data': solicitud_dieta.pk})
        else:
            errores.append('El horario para guardar la solicitud no es válida. \n Horario: %s' % str(time))

        return JsonResponse({'result': 'Error', 'Messages': errores}, status=409)


class SolicitudDietaDeleteJsonView(JsonDeleteView):
    model = SolicitudDieta

    def post(self, request, *args, **kwargs):
        # Eliminar detalles
        for detalle in DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=self.kwargs.get('pk')):
            detalle.delete()

        super().post(request, args, kwargs)
        return JsonResponse({'result': 'OK', 'id': kwargs.get('pk')})


class SolicitudDietaServidaJsonView(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador']

    def post(self, request, *args, **kwargs):
        solicitud_dieta = SolicitudDieta.objects.get(pk=kwargs.get('pk'))
        solicitud_dieta.total_dietas_servidas = self.request.POST.get('servidas', 0)
        solicitud_dieta.servida = True
        solicitud_dieta.usuario_sirvio_id = self.request.user.pk
        solicitud_dieta.save()
        return JsonResponse({'result': 'OK', 'id': kwargs.get('pk')})


class SolicitudDietaTotalDietasJsonView(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador']

    def post(self, request, *args, **kwargs):
        dietas = DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=kwargs.get('pk')).count()
        return JsonResponse({'result': 'OK', 'total': dietas})


class SolicitudDietaExcelView(DetailView):

    def link_callback(self, uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path

    def get(self, request, *args, **kwargs):        
        template = get_template('solicitudes_dietas/pdf.html')
        id = pk=kwargs.get('pk')
        detalles = []

        dietas_distintas = DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=id)\
            .values('dieta_id').distinct()

        total_dietas_solicitadas = 0
        for dieta in dietas_distintas:
            data = DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=id,
                                                        dieta_id=dieta.get('dieta_id'))
            detalle = {
                'dieta_nombre': data.first().dieta.nombre,
                'camas': data.values('no_cama'),
                'descripciones': data.values('especificar'),
                'total': data.exclude(dieta__npo=True).count(),
            }
            detalles.append(detalle)
            total_dietas_solicitadas += data.exclude(dieta__npo=True).count()

        context = {
            'solicitud_dieta': SolicitudDieta.objects.get(pk=kwargs.get('pk')),
            'total_dietas_solicitadas': total_dietas_solicitadas,
            'logo': '{}{}'.format('/var/html/static/assets/', 'img/logo-movil.png')
        }
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        pisaStatus = pisa.CreatePDF(
            html, dest=response,
            link_callback=self.link_callback
            )
        if pisaStatus.err:
            return HttpResponse('We had some errors <pre>'+ html + '</pre>')
        return response
        

    
