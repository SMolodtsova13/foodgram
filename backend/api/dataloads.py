import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('ingredients.csv', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(
                file, fieldnames=('name', 'measurement_unit')
            )
            ingredients = tuple(Ingredient(**row) for row in reader)
            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
            print('Data is load.')
