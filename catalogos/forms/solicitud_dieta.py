from django import forms

from catalogos.models import SolicitudDieta, DetalleSolicitudDieta, SolicitudDietaTiempoEstablecido
from utils.FormMixim import FieldSetModelFormMixin


class SolicitudDietaForm(FieldSetModelFormMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jornada'].widget.attrs['class'] = "select2"
        self.fields['servicio'].widget.attrs['class'] = "select2"

    class Meta:
        model = SolicitudDieta

        fields = [
            'id', 'jornada', 'servicio',
        ]


class DetalleSolicitudDietaForm(forms.ModelForm):
    especificar = forms.CharField(required=False, label='Observación*',
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dieta'].widget.attrs['class'] = "select2"

    class Meta:
        model = DetalleSolicitudDieta

        fields = {
            'id', 'dieta', 'no_cama', 'especificar'
        }


class SolicitudDietaTiempoEstablecidoForm(FieldSetModelFormMixin):
    usuario = forms.HiddenInput
    inicio = forms.DateTimeField(widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy hh:mm:ss',
                                                               'required': 'required'}))
    fin = forms.DateTimeField(widget=forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy hh:mm:ss',
                                                            'required': 'required'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].widget.attrs['readonly'] = True

    class Meta:
        model = SolicitudDietaTiempoEstablecido

        fields = [
            'id', 'no_dietas_a_solicitar', 'inicio', 'fin', 'usuario'
        ]
