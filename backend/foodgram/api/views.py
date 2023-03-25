from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response

from users.models import User
from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientRecipe, Follow,
                            Favorite, ShoppingList)
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          TagSerializer, RecipeSerializer, IngredientRecipeSerializer,
                          FollowSerializer, FavoriteSerializer, ShoppingListSerializer)
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
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
