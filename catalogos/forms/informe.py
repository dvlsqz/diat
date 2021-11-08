from crispy_forms.layout import Layout, Row, ButtonHolder, Button
from django import forms

from catalogos.models import SolicitudDieta
from utils.FormMixim import LargeFormMixin


class SolicitudesDietasForm(LargeFormMixin):
    desde = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy', 'required': 'required'}))
    hasta = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy', 'required': 'required'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row('desde', 'hasta'),
            # Row('servicio', 'jornada'),
            # Row('personal', 'usuario'),
            Row('usuario', 'jornada'),
            ButtonHolder(
                Button('filtrar', 'Filtrar', css_class='button white'),
            ),
        )

    class Meta:
        model = SolicitudDieta

        fields = [
            'id', 'servicio', 'jornada', 'usuario'
        ]


class MatrizForm(LargeFormMixin):
    desde = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy', 'required': 'required'}))
    hasta = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy', 'required': 'required'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row('desde', 'hasta'),
            ButtonHolder(
                Button('exportar', 'Exportar Matriz', css_class='button white'),
            ),
        )

    class Meta:
        model = SolicitudDieta

        fields = [
            'id',
        ]