from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

ENDPOINTS = [
    ('users', CustomUserViewSet, 'users'),
    ('ingredients', IngredientViewSet, 'ingredients'),
    ('tags', TagViewSet, 'tags'),
    ('recipes', RecipeViewSet, 'recipes'),
]

router = DefaultRouter()

for endpoint, viewset, basename in ENDPOINTS:
    router.register(endpoint, viewset, basename)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
