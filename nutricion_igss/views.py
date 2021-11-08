from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class Index(TemplateView):
    group_required = ['Administrador', 'Encargado']
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.user.is_authenticated:
            user_groups = []
            for group in request.user.groups.values_list('name', flat=True):
                user_groups.append(group)
            if len(set(user_groups).intersection(self.group_required)) <= 0:
                return HttpResponseRedirect(reverse_lazy('login'))
        else:
            return HttpResponseRedirect(reverse_lazy('login'))
        return self.render_to_response(context)
