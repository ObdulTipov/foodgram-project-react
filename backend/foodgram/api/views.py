# from django.conf import settings
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
# from rest_framework.generics import CreateAPIView
# from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientRecipe, Subscription,
                            Favorite, ShoppingCart)
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          TagSerializer, RecipeSerializer, RecipeGetSerializer,
                          RecipePostSerializer, SubscribeSerializer)
from .permissions import IsAuthorOrAdminOrReadOnly


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = kwargs['id']
        author = get_object_or_404(User, id=author_id)
        serializer = SubscribeSerializer(
            instance=author,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid() and Subscription.objects.filter(
            user=user, author=author
        ).exists() is False and user != author:
            Subscription.objects.create(
                user=user, author=author
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        user = request.user
        author_id = kwargs['id']
        subscribe = Subscription.objects.filter(user=user, author_id=author_id)

        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            following__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
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
    permission_classes = (IsAuthorOrAdminOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipePostSerializer
        return RecipeGetSerializer

    @action(
        detail=True,
        methods=['POST'],
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

        if serializer.is_valid() and Favorite.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists() is False:
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
        favorite = Favorite.objects.filter(
            user=user,
            recipe_id=recipe_id
        )

        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, **kwargs):
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

        if serializer.is_valid() and ShoppingCart.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists() is False:
            ShoppingCart.objects.create(
                user=user, recipe_id=recipe_id
            )
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['pk']
        shopping_cart = ShoppingCart.objects.filter(
            user=user,
            recipe_id=recipe_id
        )

        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = IngredientRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user,
        ).order_by('ingredient__name').values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        download_list = f'Список покупок пользователя {request.user}:\n'
        for num, (name, unit, amount) in enumerate(shopping_cart, start=1):
            download_list += f'{num}. {name} ({unit}) - {amount}\n'
        filename = 'data.txt'
        response = HttpResponse(download_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
