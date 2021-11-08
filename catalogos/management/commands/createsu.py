from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username='igss').exists():
            user = User.objects.create_superuser('igss', 'igss2019@gmail.com', '@2019.igss')
            self.stdout.write(self.style.SUCCESS('Super usuario creado'))
            admin = Group.objects.get(name="Administrador")
            admin.user_set.add(user)
