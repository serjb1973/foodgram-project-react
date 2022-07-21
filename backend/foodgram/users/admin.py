from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group

User = get_user_model()
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping, Subscribe, Tag)
from users.forms import TagForm

admin.site.unregister(Group)


class UserAdmin(DjangoUserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'last_login',
        'date_joined',
        'is_active'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    empty_value_display = '-empty-'
    verbose_name = 'Пользователи'
    fieldsets = (
        (
            "Required", {
                "fields": (
                    ('username', 'email'),
                    ('first_name', 'last_name'), 'password')
            }),
        (
            "Application", {
                "fields": ('is_active')
            }
        ),)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ['name__istartswith']
    ordering = ['name']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    pass


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
    pass


@admin.register(Shopping)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    pass


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    pass


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time',
        'image',
        'cnt_favorite')
    readonly_fields = ('cnt_favorite',)
    fieldsets = (
        (
            None, {
                "fields": (
                    ('name', 'author'),
                    ('cooking_time'))
            }
        ),
        (
            "image", {
                "fields": ('image',)
            }
        ),
        (
            "text", {
                "fields": ('text',)
            }
        ))
    search_fields = ('name__istartswith',)
    list_filter = ('author',)

    def cnt_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color')
    form = TagForm
