from django.contrib import admin

from .models import MyUser, Subscriptions


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    """Админка для пользователей."""

    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Админка для подписок."""

    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')
