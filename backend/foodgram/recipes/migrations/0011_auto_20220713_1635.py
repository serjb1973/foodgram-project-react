# Generated by Django 2.2.19 on 2022-07-13 13:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0010_recipe_ingredients'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='favorites',
            field=models.ManyToManyField(related_name='recipe_favorite_user', through='recipes.Favorite', to=settings.AUTH_USER_MODEL, verbose_name='Избраное'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='shoppings',
            field=models.ManyToManyField(related_name='recipe_shoping_user', through='recipes.Shopping', to=settings.AUTH_USER_MODEL, verbose_name='Покупки'),
        ),
    ]
