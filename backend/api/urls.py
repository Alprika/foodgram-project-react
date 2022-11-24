from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .recipes_views import IngredientViewSet, RecipeViewSet, TagViewSet
from .users_views import CustomUserViewSet

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tags")
router.register("users", CustomUserViewSet, basename="users")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
