from django.core.exceptions import PermissionDenied


class GroupRequiredMixin(object):
    """
        group_required - list of strings, required param
    """

    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_groups = []
            for group in request.user.groups.values_list('name', flat=True):
                user_groups.append(group)
            if len(set(user_groups).intersection(self.group_required)) <= 0:
                raise PermissionDenied
        else:
            raise PermissionDenied
        return super(GroupRequiredMixin, self).dispatch(request, *args, **kwargs)
