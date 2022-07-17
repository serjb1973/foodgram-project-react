from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag

BOOLEAN_CHOICES = (('0', 'False'), ('1', 'True'),)


class RecipeFilterSet(filters.FilterSet):
    """Inner backend's filter set."""

    author = filters.CharFilter(
        field_name='author',
    )
    flag = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='shopping_recipe',
        method='filter_is_favorited'
        )
    is_favorited = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='favorites',
        method='filter_is_favorited'
        )
    is_in_shopping_cart = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='shoppings',
        method='filter_is_in_shopping_cart'
        )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all())

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_anonymous:
            user = self.request.user
            if value == '1':
                return queryset.filter(favorite_recipe__user=user)
            if value == '0':
                return queryset.exclude(favorite_recipe__user=user)
        return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_anonymous:
            user = self.request.user
            if value == '1':
                return queryset.filter(shopping_recipe__user=user)
            if value == '0':
                return queryset.exclude(shopping_recipe__user=user)
        return queryset.none()

    class Meta:
        model = Recipe
        fields = ['tags']
