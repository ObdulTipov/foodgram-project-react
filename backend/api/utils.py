from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, IngredientRecipe, Recipe, Subscription
from rest_framework import status
from rest_framework.response import Response


def get_bool(self, model, obj):
    user = self.context.get('request').user

    if model == Subscription:
        if model.objects.filter(
            author_id=obj.id,
            user=user
        ).exists() and not user.is_anonymous:
            return True
        return False

    if model.objects.filter(
        recipe_id=obj.id,
        user=user
    ).exists() and not user.is_anonymous:
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
    recipe_id = kwargs['pk']
    recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
    data = {
        'id': recipe_id,
        'name': recipe_obj.name,
        'image': recipe_obj.image,
        'cooking_time': recipe_obj.cooking_time,
    }
    model_obj = model.objects.filter(
        user=user, recipe_id=recipe_id
    )

    if request.method == 'POST':
        serializer = recipeserializer(
            instance=data,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid() and model_obj.exists() is False:
            model.objects.create(
                user=user, recipe_id=recipe_id
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
