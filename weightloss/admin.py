from django.contrib import admin
from .models import Category, Post, Recipe, Challenge, UserProfile, ForumCategory, ForumTopic, ForumPost

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_on', 'is_featured')
    list_filter = ('status', 'created_on', 'is_featured')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    date_hierarchy = 'created_on'

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'calories', 'preparation_time', 'created_on', 'is_featured', 'status')
    list_filter = ('is_featured', 'created_on', 'status')
    search_fields = ('title', 'ingredients', 'instructions')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'status')
    date_hierarchy = 'created_on'

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'is_active', 'created_on')
    list_filter = ('is_active', 'created_on')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_weight', 'height', 'goal_weight', 'bmi')
    search_fields = ('user__username', 'user__email', 'bio')

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'topics_count', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_on', 'views', 'is_pinned', 'is_closed')
    list_filter = ('is_pinned', 'is_closed', 'created_on')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_pinned', 'is_closed')

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'created_on', 'is_solution')
    list_filter = ('created_on', 'is_solution')
    search_fields = ('content', 'author__username')
    list_editable = ('is_solution',)
