from django.http import JsonResponse

# Create your views here.
from django.views.generic import TemplateView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from catalogos.forms import JornadaForm
from catalogos.models import Jornada
from utils.ResponseMixim import CreateFormResponseMixin, UpdateFormResponseMixin, JsonDeleteView


class JornadasListView(TemplateView):
    template_name = 'jornadas/list.html'


class JornadasListJson(BaseDatatableView):
    model = Jornada
    columns = ['id', 'nombre', 'hora_inicio', 'hora_fin']
    order_columns = ['id', 'nombre', 'hora_inicio', 'hora_fin']


class JornadaCreateView(CreateView, CreateFormResponseMixin):
    template_name = 'jornadas/create.html'
    model = Jornada
    form_class = JornadaForm


class JornadaUpdateView(UpdateView, UpdateFormResponseMixin):
    template_name = 'jornadas/update.html'
    model = Jornada
    form_class = JornadaForm


class JornadaDeleteJsonView(JsonDeleteView):
    model = Jornada

    def post(self, request, *args, **kwargs):
        super().post(request, args, kwargs)
        return JsonResponse({'result': 'OK', 'id': kwargs.get('pk')})
