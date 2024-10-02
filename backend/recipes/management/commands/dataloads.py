import os
from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов.'

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'data/ingredients.csv')
        with open(path, 'r', encoding='utf-8') as file:
            reader = DictReader(
                file, fieldnames=('name', 'measurement_unit',)
            )
            ingredients = [
                Ingredient(
                    name=row['name'], measurement_unit=row['measurement_unit']
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
            print('Data is load.')
