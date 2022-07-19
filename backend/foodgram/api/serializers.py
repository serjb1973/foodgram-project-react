from django.db import IntegrityError, transaction
from django.db.models import Q
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping, Subscribe, Tag, User)
from rest_framework import serializers, status


class RecipeSerializerReadSimple(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time')
        model = Recipe
        ordering = ['name']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializerRead(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class UserSerializerRead(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')
        model = User
        ordering = ['id']

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            subscriber=obj
            ).exists()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=150)
    username = serializers.CharField(
        required=True,
        max_length=150)
    first_name = serializers.CharField(
        required=True,
        max_length=150)
    last_name = serializers.CharField(
        required=True,
        max_length=150)
    password = serializers.CharField(
        write_only=True,
        required=True,
        max_length=150)

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password')
        write_only_fields = ('password')
        model = User
        ordering = ['id']

    def validate(self, data):
        if self.context['request'].method == 'POST':
            username = data['username']
            email = data['email']
            if User.objects.filter(
                Q(username=username) | Q(email=email)
            ).exists():
                raise serializers.ValidationError(
                    'User and email is required to been unique',
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class FavoriteSerializerRead(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time')
        model = Recipe


class ShoppingSerializerRead(FavoriteSerializerRead):
    pass


class RecipeSerializerRead(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(
        many=True)
    author = UserSerializerRead(many=False, read_only=True)
    ingredients = RecipeIngredientSerializerRead(
        many=True,
        source='recipe_ingredient_recipe',
        read_only=False)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time')
        model = Recipe
        ordering = ['id']

    def get_is_favorited(self, obj):
        if not self.context['request'].user.is_anonymous:
            return Favorite.objects.filter(
                recipe=obj,
                user=self.context['request'].user).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        if not self.context['request'].user.is_anonymous:
            return Shopping.objects.filter(
                recipe=obj,
                user=self.context['request'].user).exists()
        else:
            return False


class RecipeSerializerWrite(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        max_length=200)
    text = serializers.CharField(
        required=True,
        max_length=8000)
    cooking_time = serializers.IntegerField(
        required=True)
    image = Base64ImageField(
        required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        read_only=False)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=False)

    class Meta:
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time')
        model = Recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        try:
            with transaction.atomic():
                recipe = Recipe.objects.create(
                    **validated_data,
                    author=self.context['request'].user)
                for tag in tags:
                    RecipeTag.objects.create(recipe=recipe, tag=tag)
                for ingredient in ingredients:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient['id'],
                        amount=ingredient['amount'])
        except IntegrityError:
            raise serializers.ValidationError(
                validated_data,
                status.HTTP_400_BAD_REQUEST)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        try:
            with transaction.atomic():
                recipe = Recipe.objects.get(id=instance.id)
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                RecipeTag.objects.filter(recipe=recipe).delete()
                for tag in tags:
                    RecipeTag.objects.create(recipe=recipe, tag=tag)
                RecipeIngredient.objects.filter(recipe=recipe).delete()
                for ingredient in ingredients:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient['id'],
                        amount=ingredient['amount'])
                recipe_new = Recipe.objects.get(id=instance.id)
        except IntegrityError:
            raise serializers.ValidationError(
                validated_data,
                status.HTTP_400_BAD_REQUEST)
        return recipe_new

    def to_representation(self, value):
        serializer = RecipeSerializerRead(value, context=self.context)
        return serializer.data


class SubscribeSerializerRead(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
            )

    def get_recipes(self, user):
        try:
            limit = int(self.context['recipes_limit'])
            recipe = Recipe.objects.filter(author=user)[:limit]
        except Exception:
            recipe = Recipe.objects.filter(author=user)
        serializer = RecipeSerializerReadSimple(
            instance=recipe,
            many=True,
            context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            author=obj,
            subscriber=self.context['request'].user
            ).exists()
