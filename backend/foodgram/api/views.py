from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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
                          TagSerializer, RecipeSerializer, FollowSerializer,
                          SignupSerializer, TokenSerializer)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


User = get_user_model()


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


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=('GET', 'PATCH'),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('role'):
            serializer.validated_data['role'] = request.user.role
        serializer.save()
        return Response(serializer.data)

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


class SignupViewSet(CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, created = User.objects.get_or_create(
            username=username, email=email
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Your authentication code',
            message='You will need it to get token\n'
                    f'confirmation_code:\n{confirmation_code}\n'
                    f'username: {username}',
            from_email=settings.FROM_EMAIL,
            recipient_list=(email,),
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(CreateAPIView):
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = request.data.get('confirmation_code')
        if default_token_generator.check_token(user, confirmation_code):
            user.is_active = True
            user.save()
            token = AccessToken.for_user(user)
            return Response(
                {'token': str(token)}, status=status.HTTP_201_CREATED
            )
        return Response(
            {'confirmation_code:': 'Incorrect confirmation code'},
            status=status.HTTP_400_BAD_REQUEST
        )
