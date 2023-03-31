from django.contrib import admin

from .models import (Ingredient, Tag, Recipe, IngredientRecipe,
                     Subscription, Favorite, ShoppingCart)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    fields = ('ingredient', 'amount',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('author', 'name', 'tags',)
    list_filter = ('author', 'name', 'tags', 'pub_date')
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Subscription)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
