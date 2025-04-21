from django.contrib import admin
from .models import Recipe, RecipeIngredient, Tag

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author']
    search_fields = ['name', 'author__username']
    inlines = [RecipeIngredientInline]
    readonly_fields = ['favorite_count']

    def favorite_count(self, obj):
        return obj.favorite_set.count()
    favorite_count.short_description = 'В избранном'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']