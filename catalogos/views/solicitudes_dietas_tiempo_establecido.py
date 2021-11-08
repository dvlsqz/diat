from django.utils import timezone

from django.contrib.auth.models import User
from django.db import transaction
from django.forms import formset_factory
from django.http import JsonResponse

from django.views.generic import TemplateView, CreateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from catalogos.forms import SolicitudDietaTiempoEstablecidoForm, SolicitudDietaForm
from catalogos.forms.solicitud_dieta import DetalleSolicitudDietaForm
from catalogos.models import SolicitudDietaTiempoEstablecido, SolicitudDieta, Dieta
from utils.PermissionsMixim import GroupRequiredMixin
from utils.ResponseMixim import CreateFormResponseMixin


class SolicitudDietasTiempoEstablecidoListView(TemplateView):
    template_name = 'solicitudes_dietas/tiempo_establecido/list.html'

    def get_context_data(self, **kwargs):
        context = super(SolicitudDietasTiempoEstablecidoListView, self).get_context_data(**kwargs)
        context['usuario'] = User.objects.filter(pk=kwargs.get('user_id')).first()
        return context


class SolicitudDietasTiempoEstablecidoListJson(BaseDatatableView):
    model = None
    columns = ['id', 'no_dietas_a_solicitar', 'inicio', 'fin']
    order_columns = ['id', 'no_dietas_a_solicitar', 'inicio', 'fin']

    def get_initial_queryset(self):
        usuario = User.objects.get(pk=self.kwargs.get('user_id'))
        return SolicitudDietaTiempoEstablecido.objects.filter(usuario=usuario)


class SolicitudDietasTiempoEstablecidoCreateView(CreateView, CreateFormResponseMixin):
    template_name = 'solicitudes_dietas/tiempo_establecido/create.html'
    model = SolicitudDietaTiempoEstablecido
    form_class = SolicitudDietaTiempoEstablecidoForm

    def get_form(self, form_class=None):
        form = super(SolicitudDietasTiempoEstablecidoCreateView, self).get_form(form_class)
        if self.kwargs.__len__() > 0:
            usuario = User.objects.get(pk=self.kwargs.get('user_id'))
            form.initial = {
                'usuario': usuario
            }
        return form


class SolicitudDietaTiempoEstablecidoCreateSolicitudView(GroupRequiredMixin, CreateView, CreateFormResponseMixin):
    group_required = ['Administrador', 'Encargado']
    template_name = 'solicitudes_dietas/tiempo_establecido/create-solicitud.html'
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

        fecha_hora = timezone.now().astimezone(tz=timezone.utc)
        item = SolicitudDietaTiempoEstablecido.objects.filter(usuario=self.request.user).last()
        inicio = item.inicio.astimezone(tz=timezone.utc)
        fin = item.fin.astimezone(tz=timezone.utc)

        if inicio < fecha_hora < fin:
            with transaction.atomic():
                # actualizar contador de dietas por tiempo establecido
                if item.no_dietas_a_solicitar is 0:
                    errores.append('El número de dietas que puede solicitar es 0')
                    return JsonResponse({'result': 'Error', 'Messages': errores}, status=409)

                item.no_dietas_a_solicitar = item.no_dietas_a_solicitar - 1
                item.save()
                # guardar datos de la solicitud
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
            errores.append('El horario no es válido.')

        return JsonResponse({'result': 'Error', 'Messages': errores}, status=409)
