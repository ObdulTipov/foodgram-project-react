from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscription, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    fields = ('ingredient', 'amount',)
    extra = 1

    def get_min_num(self, request, obj=None, **kwargs):
        return 1


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'name', 'author', 'favorite_count')
    list_display_links = ('image_tag', 'name',)
    readonly_fields = ('image_tag',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags', 'pub_date')
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Subscription)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
