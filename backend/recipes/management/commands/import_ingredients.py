import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Заполнение БД'

    def handle(self, *args, **kwargs):
        with open('./data/ingredients.csv',
                  newline='', encoding='UTF-8') as file:
            file_reader = csv.reader(file)
            for row in file_reader:
                name, measurement_unit = row
                if name != 'name':
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )

        self.stdout.write(self.style.SUCCESS('Successfully'))
