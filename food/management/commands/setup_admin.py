from django.contrib.auth.models import User as AuthUser
from django.core.management.base import BaseCommand

from food.models import User


class Command(BaseCommand):
    help = 'Create or update Django admin and app staff users'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='Khushi@Krishna')
        parser.add_argument('--password', default='Khushi')
        parser.add_argument('--email', default='khushi@krishna.com')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        auth_user, created = AuthUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        auth_user.email = email
        auth_user.is_staff = True
        auth_user.is_superuser = True
        auth_user.set_password(password)
        auth_user.save()

        app_user, app_created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': 'Khushi Krishna',
                'mobile_number': '9999999999',
                'password': password,
                'is_staff': True,
            },
        )
        app_user.name = 'Khushi Krishna'
        app_user.password = password
        app_user.is_staff = True
        app_user.save()

        self.stdout.write(self.style.SUCCESS(
            f'Django admin user ready: username="{username}" password="{password}"'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'App admin login ready: email="{email}" password="{password}"'
        ))
        self.stdout.write('Use /admin/ for Django admin and /login/ for app admin dashboard.')
