
from catalogos.models import Servicio
from utils.FormMixim import FieldSetModelFormMixin


class ServicioForm(FieldSetModelFormMixin):
    class Meta:
        model = Servicio

        fields = [
            'id', 'nombre'
        ]
