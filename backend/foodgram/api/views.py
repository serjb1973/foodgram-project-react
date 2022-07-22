import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from api.filters import RecipeFilterSet
from api.pagination import ApiPagination
from api.serializers import (FavoriteSerializerRead, IngredientSerializer,
                             RecipeSerializerRead, RecipeSerializerWrite,
                             ShoppingSerializerRead, SubscribeSerializerRead,
                             TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping, Subscribe, Tag, User)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all().order_by('slug')
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset1 = queryset.filter(name__istartswith=name)
            queryset2 = queryset.filter(
                name__icontains=name).difference(queryset1)
            return queryset1.union(queryset2, all=True)
        return queryset


class SubscribeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscribeSerializerRead
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return User.objects.filter(
            subscribe_author__subscriber_id=self.request.user.id).order_by(
                'username')
        
    def get_serializer_context(self):
        context = super(SubscribeViewSet, self).get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit:
            context.update({"recipes_limit": recipes_limit})
        return context


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    pagination_class = ApiPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeSerializerWrite
        return RecipeSerializerRead

    @action(detail=True, methods=['delete'])
    def delete_recipe(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='download_shopping_cart')
    def shopping_list(self, request):
        # Create the HttpResponse object with the appropriate header.
        response = HttpResponse(content_type='text/plain; charset=utf8')
        response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
        report = []
        report.append('Список покупок')
        report.append(
            f'{datetime.datetime.now():%Y-%m-%d} {request.user.username}')
        report.append('# Наименование Ед.Измерения Количество')
        queryset = RecipeIngredient.objects.filter(
            recipe__shopping_recipe__user=request.user.id).values(
                 'ingredient__name',
                 'ingredient__measurement_unit').annotate(
                    amount_sum=Sum('amount')).order_by('ingredient__name')
        idx = 0
        for rec in queryset:
            name = rec['ingredient__name'].capitalize()
            measurement_unit = rec['ingredient__measurement_unit']
            measurement_unit = f'({measurement_unit})'
            idx += 1
            report.append(
                f'{idx} * {name} {measurement_unit} - {rec["amount_sum"]}')
        response.write('\n'.join(report))
        return response


@api_view(['POST', 'DELETE'])
def subscribe_change(request, author_id):
    author = get_object_or_404(User, id=author_id)
    try:
        if request.method == 'POST':
            Subscribe.objects.create(subscriber=request.user, author=author)
    except Exception:
        return Response(
            {'detail': 'Ошибка подписки'},
            status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        subscribe = Subscribe.objects.filter(
            subscriber=request.user,
            author=author)
        if subscribe:
            subscribe.delete()
        else:
            return Response(
                {'detail': 'Нет подписки'},
                status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        serializer = SubscribeSerializerRead(
            author,
            context={'request': request})
        return Response(serializer.data)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
def favorite_change(request, id):
    try:
        user = User.objects.get(username=request.user)
    except Exception:
        return Response(
            {'detail': 'Пользователь не авторизован.'},
            status=status.HTTP_401_UNAUTHORIZED)
    recipe = get_object_or_404(Recipe, id=id)
    try:
        if request.method == 'POST':
            Favorite.objects.create(recipe=recipe, user=user)
    except Exception:
        return Response(
            {'detail': 'Ошибка добавления в избранное'},
            status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            Favorite.objects.filter(recipe=recipe, user=user).delete()
        else:
            return Response(
                {'detail': 'Ошибка удаления из избранного'},
                status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        serializer = FavoriteSerializerRead(
            recipe,
            context={'request': request})
        return Response(serializer.data)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
def shopping_change(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    try:
        if request.method == 'POST':
            Shopping.objects.create(recipe=recipe, user=request.user)
    except Exception:
        return Response(
            {'detail': 'Ошибка добавления в список покупок'},
            status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        if Shopping.objects.filter(recipe=recipe, user=request.user).exists():
            Shopping.objects.filter(recipe=recipe, user=request.user).delete()
        else:
            return Response(
                {'detail': 'Ошибка удаления из списка покупок'},
                status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        serializer = ShoppingSerializerRead(
            recipe,
            context={'request': request})
        return Response(serializer.data)
    return Response(status=status.HTTP_204_NO_CONTENT)
