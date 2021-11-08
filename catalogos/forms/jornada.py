from catalogos.models import Jornada
from utils.FormMixim import FieldSetModelFormMixin


class JornadaForm(FieldSetModelFormMixin):
    class Meta:
        model = Jornada

        fields = [
            'id', 'nombre', 'hora_inicio', 'hora_fin'
        ]
