from django.http import JsonResponse

# Create your views here.
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django_datatables_view.base_datatable_view import BaseDatatableView

from catalogos.forms import DietaForm
from catalogos.models import Dieta
from utils.ResponseMixim import CreateFormResponseMixin, UpdateFormResponseMixin, JsonDeleteView
from django.contrib.humanize.templatetags.humanize import intcomma


class DietasListView(TemplateView):
    template_name = 'dietas/list.html'


class DietasListJson(BaseDatatableView):
    dietas = None
    columns = ['id', 'nombre', 'npo', 'viaje']
    order_columns = ['id', 'nombre', 'npo', 'viaje']

    def get_initial_queryset(self):
        return Dieta.objects.all()

    def render_column(self, row, column):
        if column == 'precio':
            precio = round(float(row.precio), 2)
            return "Q %s%s" % (intcomma(int(precio)), ("%0.2f" % precio)[-3:])
        if column == 'npo':
            if row.npo:
                return 'Si'
            else:
                return 'No'
        if column == 'viaje':
            if row.viaje:
                return 'Si'
            else:
                return 'No'
        else:
            return super().render_column(row, column)

    def post(self, request, *args, **kwargs):
        self.dietas = Dieta.objects.all()
        if kwargs.__len__() > 0:
            dietas_json = [ob.as_json_basico() for ob in self.dietas]
            return JsonResponse({'data': dietas_json})
        else:
            return super().post(request, args, kwargs)


class DietaCreateView(CreateView, CreateFormResponseMixin):
    template_name = 'dietas/create.html'
    model = Dieta
    form_class = DietaForm


class DietaUpdateView(UpdateView, UpdateFormResponseMixin):
    template_name = 'dietas/update.html'
    model = Dieta
    form_class = DietaForm


class DietaDeleteJsonView(JsonDeleteView):
    model = Dieta

    def post(self, request, *args, **kwargs):
        super().post(request, args, kwargs)
        return JsonResponse({'result': 'OK', 'id': kwargs.get('pk')})


class DietaGetView(UpdateView, JsonResponse):
    def get(self, request, *args, **kwargs):
        json = Dieta.objects.get(pk=kwargs.get('pk')).as_json_basico()
        return JsonResponse(json)
