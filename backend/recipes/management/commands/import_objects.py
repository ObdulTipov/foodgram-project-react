import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загрузка данных в базу из ingredients.csv и tags.csv'

    def handle(self, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'data/ingredients.csv'),
                  'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            ingredients_to_add = [Ingredient(name=row[0],
                                  measurement_unit=row[1]) for row in reader]
            Ingredient.objects.bulk_create(ingredients_to_add)

        with open(os.path.join(settings.BASE_DIR, 'data/tags.csv'),
                  'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            tags_to_add = [Tag(name=row[0],
                           color=row[1],
                           slug=row[2]) for row in reader]
            Tag.objects.bulk_create(tags_to_add)

        return (
            f'Ингредиентов в БД: {Ingredient.objects.count()}\n'
            f'Тегов в БД: {Tag.objects.count()}'
        )
