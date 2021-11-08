from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView
from django_datatables_view.base_datatable_view import BaseDatatableView

from catalogos.forms import UserForm, UserEditForm
from utils.PermissionsMixim import GroupRequiredMixin
from utils.ResponseMixim import CreateFormResponseMixin, UpdateFormResponseMixin, JsonDeleteView
from django.contrib.messages.views import SuccessMessageMixin


class UsersListView(GroupRequiredMixin, TemplateView):
    group_required = ['Administrador']
    template_name = 'usuarios/list.html'


class UsersListJson(GroupRequiredMixin, BaseDatatableView):
    group_required = ['Administrador']
    model = User
    columns = ['id', 'username', 'is_active']
    order_columns = ['id', 'username', 'is_active']

    def get_initial_queryset(self):
        return User.objects.filter(is_superuser=False)

    def render_column(self, row, column):
        if column == 'is_active':
            if row.is_active:
                return '<span class="badge badge-success" onclick="cambiarEstado(%s)">Activo</span>' % row.pk
            else:
                return '<span class="badge badge-danger" onclick="cambiarEstado(%s)">Inactivo</span>' % row.pk
        else:
            return super().render_column(row, column)


class UserCreateView(GroupRequiredMixin, SuccessMessageMixin, CreateView, CreateFormResponseMixin):
    group_required = ['Administrador']
    template_name = 'usuarios/create.html'
    model = User
    form_class = UserForm
    success_url = reverse_lazy('catalogos:users')
    success_message = "Registro guardado"

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                is_active=True
            )
            grupo = form.cleaned_data['groups']
            grupo.user_set.add(user)
        return HttpResponseRedirect(self.success_url)


class UserUpdateView(GroupRequiredMixin, UpdateView, UpdateFormResponseMixin, SuccessMessageMixin):
    group_required = ['Administrador']
    template_name = 'usuarios/update.html'
    model = User
    form_class = UserEditForm
    success_url = reverse_lazy('catalogos:users')
    success_message = "Registro actualizado"

    def get_initial(self):
        self.initial = {
            'username': self.object.username,
            'first_name': self.object.first_name,
            'last_name': self.object.last_name,
            'email': self.object.email,
        }

        return self.initial.copy()

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.get(pk=self.kwargs.get('pk'))
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

        return HttpResponseRedirect(self.success_url)


class UserDeleteJsonView(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador']

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs.get('pk'))
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return JsonResponse({'result': 'OK', 'id': kwargs.get('pk')})


class UserDetailsView(GroupRequiredMixin, DetailView):
    group_required = ['Administrador', 'Encargado']
    model = User
    template_name = 'usuarios/details.html'
