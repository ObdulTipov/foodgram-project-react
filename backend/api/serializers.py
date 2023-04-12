from django.contrib.auth import get_user_model
from django.db import models
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)
from rest_framework import serializers

from .utils import create_update_recipe, get_bool

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
        return get_bool(self, Subscription, obj)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientRecipe
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeMiniSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        required=False, allow_null=True, use_url=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class RecipeSerializer(RecipeMiniSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeMiniSerializer.Meta):
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=models.F('ingredient_recipe__amount')
        )

    def get_is_favorited(self, obj):
        return get_bool(self, Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return get_bool(self, ShoppingCart, obj)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        name = self.initial_data.get('name')
        cooking_time = self.initial_data.get('cooking_time')

        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Выберите ингридиенты.'
            )

        ingredients_id = []
        for ingredient in ingredients:
            id = ingredient.get('id')
            if not Ingredient.objects.filter(id=id).exists():
                raise serializers.ValidationError(
                    f'Ингредиента с id: {id}, нет.'
                )
            if id in ingredients_id:
                raise serializers.ValidationError(
                    f'{ingredient} уже добавлен.'
                )
            if ingredient.get('amount') in (None, 0):
                raise serializers.ValidationError(
                    'Введите количество ингредиента.'
                )
            ingredients_id.append(id)

        if len(tags) == 0:
            raise serializers.ValidationError(
                'Выберите Теги.'
            )

        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    f'Тега с id: {tag}, нет.'
                )

        data.update({
            'ingredients': ingredients,
            'tags': tags,
            'name': name,
            'cooking_time': cooking_time,
        })

        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        name = validated_data.get('name')
        if Recipe.objects.filter(
            author=author,
            name=name
        ).exists():
            raise serializers.ValidationError(
                f'Рецепт с названием {name} уже добавлен.'
            )
        return create_update_recipe(validated_data, author=author)

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients = IngredientRecipe.objects.filter(
            recipe_id=instance.id
        )
        ingredients.delete()
        create_update_recipe(validated_data, instance=instance)
        instance.save()
        return instance


class SubscribeSerializer(CustomUserSerializer):
    recipes = RecipeMiniSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username')

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance

        if user == author:
            raise serializers.ValidationError(
                'Подпишитесь на кого нибудь другого'
            )
        if Subscription.objects.filter(
            user=user, author=author
        ).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на пользователя: {author}.'
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
