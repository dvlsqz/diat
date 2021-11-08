from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django import forms
from django.contrib.auth import password_validation

from utils.FormMixim import FieldSetModelFormMixin
from utils.validators import numeric_valid


class PermissionsModelMultipleChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name


class UserForm(FieldSetModelFormMixin, UserCreationForm):
    username = forms.CharField(max_length=10, label="IBM", validators=[numeric_valid],
                               help_text='<p>10 digitos maximo.</p>')

    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Repita la contraseña para su verificación",
    )

    groups = forms.ModelChoiceField(label='Rol', queryset=Group.objects.all())

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'groups',
        ]


class UserEditForm(FieldSetModelFormMixin, forms.ModelForm):
    username = forms.CharField(max_length=10, label="IBM", validators=[numeric_valid],
                               help_text='<p>10 digitos maximo.</p>')

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        ]
