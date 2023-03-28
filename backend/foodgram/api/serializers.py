from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserSerializer

from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientRecipe, Follow,
                            Favorite, ShoppingList)


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if Follow.objects.filter(
            author_id=obj.id,
            user=user
        ).exists():
            return True
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if Favorite.objects.filter(
            recipe_id=obj.id,
            user=user
        ).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if ShoppingList.objects.filter(
            recipe_id=obj.id,
            user=user
        ).exists():
            return True
        return False

    def to_internal_value(self, validated_data):
        pass

    def create(self, validated_data):
        author = self.context.get('request').user
        recipe = self.validated_data.get('name')

        if Recipe.objects.filter(
            author=author,
            name=recipe
        ).exists():
            raise serializers.ValidationError(
                f'Рецепт {recipe} уже добавлен.'
            )

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientin_recipe')

        recipe = Recipe.objects.create(author=author, **validated_data)

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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'
