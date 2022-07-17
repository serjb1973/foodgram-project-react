import json

from django.core.management import BaseCommand

from recipes.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Show this if the data already exist in the database
        if (Ingredient.objects.count() > 0):
            print('data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        # Show this before loading the data into the database
        print("Loading all data...")
        data = open('../../data/ingredients.json', encoding='utf-8').read()
        json_data = json.loads(data)
        # Code to load the data into database
        for row in json_data:
            ingredient = Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit'])
            ingredient.save()
        print('...done')
