from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import os
import environ


class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not User.objects.filter(username=os.environ['CREATESU_NAME']).exists():
            User.objects.create_superuser(
                username=os.environ['CREATESU_NAME'],
                password=os.environ['CREATESU_PASS']
            )
        print('Superuser has been created.')