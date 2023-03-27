from django.contrib import admin

from .models import (Ingredient, Tag, Recipe, IngredientRecipe,
                     Follow, Favorite, ShoppingList)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit',)
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
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
