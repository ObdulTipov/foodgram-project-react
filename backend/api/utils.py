from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, IngredientRecipe, Recipe, Subscription
from rest_framework import status
from rest_framework.response import Response


def get_bool(self, model, obj):
    user = self.context.get('request').user

    if user.is_anonymous:
        return False

    if model == Subscription:
        if model.objects.filter(
            author=obj,
            user=user
        ).exists():
            return True
        return False

    if model.objects.filter(
        recipe=obj,
        user=user
    ).exists():
        return True
    return False


def create_update_recipe(validated_data, author=None, instance=None):
    tags = validated_data.pop('tags')
    ingredients = validated_data.pop('recipe_ingredient')

    if instance is None:
        recipe = Recipe.objects.create(author=author, **validated_data)
    else:
        recipe = instance

    recipe.tags.set(tags)

    IngredientRecipe.objects.bulk_create([
        IngredientRecipe(
            recipe=recipe,
            amount=ingredient.get('amount'),
            ingredient=Ingredient.objects.get(
                id=ingredient.get('id')
            ),
        ) for ingredient in ingredients
    ])

    return recipe


def post_or_del_view(request, model, recipeserializer, **kwargs):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
    data = {
        'id': recipe.id,
        'name': recipe.name,
        'image': recipe.image,
        'cooking_time': recipe.cooking_time,
    }
    model_obj = model.objects.filter(
        user=user, recipe=recipe
    )

    if request.method == 'POST':
        serializer = recipeserializer(
            instance=data,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        if model_obj.exists() is False:
            model.objects.get_or_create(
                user=user, recipe=recipe
            )
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

    if request.method == 'DELETE':
        if model_obj.exists():
            model_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
