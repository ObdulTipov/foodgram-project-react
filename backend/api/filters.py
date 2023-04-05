from django_filters import rest_framework as filters
from recipes.models import Favorite, Recipe, ShoppingCart, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_subscribed = filters.BooleanFilter(
        method='filter_is_subscribed'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user

        if Favorite.objects.filter(user=user).exists():
            return queryset.filter(favorite_recipe__user=user)

        return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user

        if ShoppingCart.objects.filter(user=user).exists():
            return queryset.filter(shoppingcart_recipe__user=user)

        return queryset.none()

    def filter_is_subscribed(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(author=user)
