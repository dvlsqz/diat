from django.core.validators import RegexValidator

numeric_valid = RegexValidator(r'^[0-9]*$', 'Solo se aceptan digitos.')
