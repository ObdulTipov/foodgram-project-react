from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tag = filters.CharFilter(
        field_name='name',
    )

    class Meta:
        model = Recipe
        fields = ('tag',)
