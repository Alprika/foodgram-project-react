from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = (
        'name',
    )
    list_filter = ('measurement_unit',)


@admin.register(IngredientInRecipe)
class LinksAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
        'pub_date',
        'count_favorite'
    )
    list_filter = (
        "author",
        "name",
        "tags",
    )
    search_fields = ('author__username', 'name',)

    def count_favorite(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = ('user',)
    list_filter = ('user',)
