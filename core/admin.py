from django.contrib import admin
from .models import User, Task, Review, Category, Report

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    actions = ['ban_users', 'unban_users']

    def ban_users(self, request, queryset):
        queryset.update(is_active=False)
    ban_users.short_description = "Забанить выбранных пользователей"

    def unban_users(self, request, queryset):
        queryset.update(is_active=True)
    unban_users.short_description = "Разбанить выбранных пользователей"

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'fund', 'created_at', 'is_completed')
    search_fields = ('title', 'description')
    list_filter = ('is_completed',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'target', 'rating', 'created_at')
    search_fields = ('author__username', 'target__username', 'comment')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(Report)
