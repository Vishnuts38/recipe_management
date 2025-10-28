from django.contrib import admin
from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    list_filter = ('user',)
    ordering = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'category', 'user', 'description')
    list_filter = ('user', 'category', 'date')
    search_fields = ('description', 'category__name', 'user__username', 'user__email')
    autocomplete_fields = ('category',)
    date_hierarchy = 'date'
