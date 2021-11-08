from catalogos.models import Dieta
from utils.FormMixim import FieldSetModelFormMixin


class DietaForm(FieldSetModelFormMixin):
    class Meta:
        model = Dieta

        fields = [
            'id', 'nombre'
        ]
