from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Delete user data...")
        Ingredient.objects.all().delete()
        print("...done")
