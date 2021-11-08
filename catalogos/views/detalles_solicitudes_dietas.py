from django.views.generic import CreateView

from catalogos.forms.solicitud_dieta import DetalleSolicitudDietaForm
from catalogos.models import DetalleSolicitudDieta
from utils.ResponseMixim import CreateFormResponseMixin


class DetalleSolicitudDietaCreateView(CreateView, CreateFormResponseMixin):
    template_name = 'solicitudes_dietas/detalle_solicitud_create.html'
    model = DetalleSolicitudDieta
    form_class = DetalleSolicitudDietaForm
