from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset
from django import forms


class FieldSetModelFormMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_names = self.fields.keys()
        self.helper = FormHelper(self)
        self.helper.html5_required = True
        self.helper.label_class = 'col-lg-3 col-form-label'
        self.helper.field_class = 'col-lg-9'
        self.helper.wrapper_class = 'form-group row'
        self.helper.form_tag = False

    def set_legend(self, text):
        self.helper.layout = Fieldset(text, *self.field_names)

    def set_action(self, action):
        self.helper.form_action = action


class LargeFormMixin(FieldSetModelFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.label_class = 'col-lg-3 col-xl-4 col-form-label'
        self.helper.field_class = 'col-lg-9 col-xl-8'
        self.helper.wrapper_class = 'form-group row col-lg-12 col-xl-6'
