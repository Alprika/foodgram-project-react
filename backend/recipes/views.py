from api.filters import IngredientInRecipe, RecipeFilter
from api.pagination import RecipePagination
from api.permissions import IsAdminOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, ShortRecipeSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientInRecipe
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _do_post_method(self, request, model, error_data):
        user = request.user
        recipe = self.get_object()
        if model.objects.filter(
                user=user,
                recipe=recipe,
        ).exists():
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(
            user=user,
            recipe=recipe,
        )
        serializer = ShortRecipeSerializer(
            recipe,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _do_delete_method(self, request, model, error_data):
        user = request.user
        recipe = self.get_object()
        favorite = model.objects.filter(
            user=user,
            recipe=recipe,
        )
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        model = Favorite
        if request.method == 'POST':
            error_data = {'errors': 'Рецепт добавлен в избранное'}
            return self._do_post_method(request, model, error_data)
        error_data = {'errors': 'Рецепт удален из избранного'}
        return self._do_delete_method(request, model, error_data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        model = ShoppingCart
        if request.method == 'POST':
            error_data = {'errors': 'Рецепт уже добавлен в корзину'}
            return self._do_post_method(request, model, error_data)
        error_data = {'errors': 'Рецепт уже удален из корзины'}
        return self._do_delete_method(request, model, error_data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredient_queryset = IngredientInRecipe.objects.filter(
            recipes__shoppingcart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            ingredient_sum=Sum('amount')
        ).values_list(
            'ingredient__name',
            'ingredient_sum',
            'ingredient__measurement_unit',
        )
        shopping_cart = {}
        for item in ingredient_queryset:
            name = item[0]
            if name not in shopping_cart:
                shopping_cart[name] = {
                    'amount': item[1],
                    'measurement_unit': item[2],
                }
        filename = 'hopping_list.txt'
        shopping_cart_text = 'Список покупок: '
        for list_number, (name, data) in enumerate(shopping_cart.items(), 1):
            shopping_cart_text += (
                f'{list_number}. {name} - {data["amount"]} '
                f'{data["measurement_unit"]}'
            )
        response = HttpResponse(
            shopping_cart_text, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
