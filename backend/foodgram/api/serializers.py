from rest_framework import serializers
from django.contrib.auth import get_user_model
# from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserSerializer
from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientRecipe, Follow,
                            Favorite, ShoppingList)
from .validators import validate_username


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientRecipe
        fields = '__all__'


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


class CustomUserSerializer(UserSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )
    email = serializers.EmailField(
        max_length=254,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User
        lookup_field = 'username'


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=(
            validate_username,
            UniqueValidator(queryset=User.objects.all())
        ),
        required=True
    )
    email = serializers.EmailField(
        max_length=254,
        validators=(UniqueValidator(queryset=User.objects.all()),),
        required=True
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already in use')
        return value

    class Meta:
        model = User
        fields = ('email', 'username')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
