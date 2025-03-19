import django_filters
from recipe.models import Recipe


class Recipe_Filter(django_filters.FilterSet):
    is_favorited = django_filters.filters.NumberFilter(
        method="is_recipe_in_favorites_filter"
    )
    is_in_shopping_cart = django_filters.filters.NumberFilter(
        method="is_recipe_in_shoppingcart_filter"
    )

    def is_recipe_in_favorites_filter(self, queryset, name, value):
        user = self.request.user
        if value in (0, 1) and user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=user)
            else:
                return queryset.exclude(favorites__user=user)
        return queryset

    def is_recipe_in_shoppingcart_filter(self, queryset, name, value):
        user = self.request.user
        if value in (0, 1) and user.is_authenticated:
            if value:
                return queryset.filter(in_cart__user=user)
            else:
                return queryset.exclude(in_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "is_favorited", "is_in_shopping_cart")
