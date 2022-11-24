from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers

from .users_serializers import CustomUserSerializer

User = get_user_model()


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
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    validators = (
        validators.UniqueTogetherValidator(
            queryset=IngredientInRecipe.objects.all(),
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
        request = self.context['request'].user
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
        model = IngredientInRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Должен быть хотя бы один ингредиент!')
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError('Ингредиенты должны быть уникальными!')
            try:
                amount = int(item['amount'])
                if amount <= 0:
                    raise ValidationError(
                        'Количество ингредиента должно быть больше нуля!')
            except ValueError:
                raise ValidationError('Должно быть число - ошибка')
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Выберите хотя бы один тег!')
        for tag in value:
            if tag not in Tag.objects.all():
                raise ValidationError('Тег не найден!')
        tags_set = set(value)
        if len(value) != len(tags_set):
            raise ValidationError(
                'Теги должны быть уникальными!')
        return value

    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data



class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if request.user.shoping_cart_user.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Выбранный рецепт уже добавлен в список покупок!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance.recipe, context=context).data
