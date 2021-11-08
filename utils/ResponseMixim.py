from django.views.generic.edit import ModelFormMixin
from django.http import JsonResponse
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeletionMixin


class CreateFormResponseMixin(ModelFormMixin):
    def form_valid(self, form):
        # Guardamos y volvemos a mostrar el formulario vacio
        form.save()
        return self.render_to_response(self.get_context_data(form=form))


class UpdateFormResponseMixin(ModelFormMixin):
    def form_valid(self, form):
        # Guardamos y volvemos a mostrar el formulario vacio
        # noinspection PyAttributeOutsideInit
        self.object = form.save()
        return self.render_to_response(self.get_context_data())


class JsonDeleteView(SingleObjectMixin, DeletionMixin, View):
    """
    Permite borrar una instrancia de un objeto devolviendo unicamente un JSON como respuesta
    """
    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'result': 'OK'})
