from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from users.serializers import CustomUserSerializer
from .models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    validators = (
        validators.UniqueTogetherValidator(
            queryset=IngredientsInRecipe.objects.all(),
            fields=('ingredient', 'recipe')
        ),
    )

class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = CustomUserSerializer(required=False)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        required=False,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'cooking_time'
        )

    def in_list(self, model, obj):
        request = self.context["request"].user
        if request is None or request.user.is_anonymous:
            return False
        return (
            request.is_authenticated
            and model.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )

    def get_is_favorited(self, obj):
        return self.in_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.in_list(obj, ShoppingCart)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class IngredientsInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
    )
    ingredients = IngredientsInRecipeWriteSerializer(
        many=True,
    )
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time'
        )

    def _add_tags_and_ingredients(self, recipe, tags_data, ingredients_data):
        recipe.tags.set(tags_data)
        recipe.ingredients.set(IngredientsInRecipe.objects.bulk_create([
            IngredientsInRecipe(
                ingredient=item.get('ingredient'),
                amount=item.get('amount'),
            ) for item in ingredients_data
        ]))
        return recipe

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        return self._add_tags_and_ingredients(
            recipe, tags_data, ingredients_data
        )

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        super(RecipeCreateSerializer, self).update(instance, validated_data)
        return self._add_tags_and_ingredients(
            instance, tags_data, ingredients_data
        )
