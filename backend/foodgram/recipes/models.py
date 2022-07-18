from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Creation a ingredients name for recipe.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Наименование ингредиента')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения')

    def __str__(self):
        return str(self.id)


class Tag(models.Model):
    """Creation a tag's object for finding. """

    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        db_index=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет')
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг',
        db_index=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Creation a recipe."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор',
        db_index=True
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Наименование рецепта')
    image = models.ImageField(
        null=False,
        verbose_name='Картинка',
        upload_to='recipe',
        blank=True)
    text = models.CharField(
        max_length=8000,
        verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MaxValueValidator(14400),
            MinValueValidator(1)
        ],
        verbose_name='Время приготовления (в минутах)')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        through='RecipeTag'
    )
    favorites = models.ManyToManyField(
        User,
        verbose_name='Избраное',
        related_name='recipe_favorite_user',
        through='Favorite'
    )
    shoppings = models.ManyToManyField(
        User,
        verbose_name='Покупки',
        related_name='recipe_shoping_user',
        through='Shopping'
    )

    def __str__(self):
        return str(self.id)


class Favorite(models.Model):
    """Creation a favorite object,
    which is an inner bonded object to Recipe and User instances.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь',
        db_index=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Subscribe(models.Model):
    """Creation a subscribe object,
    which is an inner bonded object to User(subscriber)
    and User(author) instances.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe_author',
        verbose_name='Автор'
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe_subscriber',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_author_subscriber'),
            models.CheckConstraint(
                check=~models.Q(author=models.F('subscriber')),
                name='author_not_subscriber_to_themselves'
            )]

    def __str__(self):
        return f'{self.author} {self.subscriber}'


class Shopping(models.Model):
    """Creation a subscribe object,
    which is an inner bonded object to shopping User and Recipe instances.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Покупатель',
        db_index=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shopping'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class RecipeIngredient(models.Model):
    """Creation a recipe object,
    which is an inner bonded object to Recipe and Ingredient instances.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient_recipe',
        verbose_name='Рецепт',
        db_index=True
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient_ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество',
        null=False,
        blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'


class RecipeTag(models.Model):
    """Creation a recipe object,
    which is an inner bonded object to Recipe and Tag instances.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag_recipe',
        verbose_name='Рецепт',
        db_index=True
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag_tag',
        verbose_name='Тег'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.tag}'
