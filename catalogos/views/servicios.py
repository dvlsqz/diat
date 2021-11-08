from django.http import JsonResponse

# Create your views here.
from django.views.generic import TemplateView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from catalogos.forms import ServicioForm
from catalogos.models import Servicio
from utils.ResponseMixim import CreateFormResponseMixin, UpdateFormResponseMixin, JsonDeleteView


class ServiciosListView(TemplateView):
    template_name = 'servicios/list.html'


class ServiciosListJson(BaseDatatableView):
    model = Servicio
    columns = ['id', 'nombre']
    order_columns = ['id', 'nombre']


class ServicioCreateView(CreateView, CreateFormResponseMixin):
    template_name = 'servicios/create.html'
    model = Servicio
    form_class = ServicioForm


class ServicioUpdateView(UpdateView, UpdateFormResponseMixin):
    template_name = 'servicios/update.html'
    model = Servicio
    form_class = ServicioForm


class ServicioDeleteJsonView(JsonDeleteView):
    model = Servicio

    def post(self, request, *args, **kwargs):
        super().post(request, args, kwargs)
        return JsonResponse({'result': 'OK', 'id': kwargs.get('pk')})
