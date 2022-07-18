from api.views import (IngredientViewSet, RecipeViewSet, SubscribeViewSet,
                       TagViewSet, favorite_change, shopping_change,
                       subscribe_change)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

# version 1
router1 = DefaultRouter()
router1.register(r'recipes', RecipeViewSet, basename='recipes')
router1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router1.register(r'subscriptions', SubscribeViewSet, basename='subscriptions')
router1.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('users/subscriptions/', SubscribeViewSet.as_view({'get': 'list'})),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router1.urls)),
    path('users/<int:author_id>/subscribe/', subscribe_change),
    path('recipes/<int:id>/favorite/', favorite_change),
    path('recipes/<int:id>/shopping_cart/', shopping_change)
]
