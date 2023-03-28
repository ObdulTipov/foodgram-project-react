from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientRecipe, Follow,
                            Favorite, ShoppingList)
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          TagSerializer, RecipeSerializer, FollowSerializer)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def follow(self, request, **kwargs):
        user = request.user
        author_id = kwargs['id']
        author_obj = get_object_or_404(User, id=author_id)
        serializer = FollowSerializer(
            instance=author_obj,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            Follow.objects.create(
                user=user, author_id=author_id
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @follow.mapping.delete
    def delete_follow(self, request, **kwargs):
        user = request.user
        author_id = kwargs['id']

        if get_object_or_404(
            Follow,
            user=user,
            author_id=author_id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def followings(self, request):
        followings_data = User.objects.filter(
            following__user=request.user
        )
        page = self.paginate_queryset(followings_data)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    # filterset_class = IngredientFilter
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)

    @action(
        detail=True,
        methods=('POST'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['pk']
        recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
        data = {
            'id': recipe_id,
            'name': recipe_obj.name,
            'image': recipe_obj.image,
            'cooking_time': recipe_obj.cooking_time,
        }
        serializer = RecipeSerializer(
            instance=data,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            Favorite.objects.create(
                user=user, recipe_id=recipe_id
            )
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['pk']

        if get_object_or_404(
            Favorite,
            user=user,
            recipe_id=recipe_id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_list(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['pk']
        recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
        data = {
            'id': recipe_id,
            'name': recipe_obj.name,
            'image': recipe_obj.image,
            'cooking_time': recipe_obj.cooking_time,
        }
        serializer = RecipeSerializer(
            instance=data,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            ShoppingList.objects.create(
                user=user, recipe_id=recipe_id
            )
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @shopping_list.mapping.delete
    def delete_shopping_list(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['pk']

        if get_object_or_404(
            ShoppingList,
            user=user,
            recipe_id=recipe_id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_list(self, request):
        shopping_list = IngredientRecipe.objects.filter(
            recipe__shoppinglist_recipe__user=request.user,
        ).order_by('ingredient__name').values_list(
            'ingredient__name',
            'ingredient__unit'
        ).annotate(amount=Sum('amount'))

        download_list = f'Список покупок {request.user}:\n'
        for num, (name, unit, amount) in enumerate(shopping_list, start=1):
            download_list += f'\n {num}. {name} - {amount} {unit}'
        filename = 'data.txt'
        response = HttpResponse(download_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
