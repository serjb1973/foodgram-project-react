from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag

BOOLEAN_CHOICES = (('0', 'False'), ('1', 'True'),)


class RecipeFilterSet(filters.FilterSet):
    """Inner backend's filter set."""

    author = filters.CharFilter(
        field_name='author',)
    flag = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='shopping_recipe',
        method='filter_is_favorited')
    is_favorited = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='favorite_recipe',
        method='filter_add')
    is_in_shopping_cart = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='shopping_recipe',
        method='filter_add')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all())
    is_test = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='favorite_recipe',
        method='filter_add')

    def filter_add(self, queryset, name, value):
        if not self.request.user.is_anonymous:
            user = self.request.user
            if value == '1':
                return queryset.filter(**{f'{name}__user': user})
            else:
                return queryset.exclude(**{f'{name}__user': user})
        return queryset.none()

    class Meta:
        model = Recipe
        fields = ['tags']
