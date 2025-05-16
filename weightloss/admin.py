from django.contrib import admin
from .models import Category, Post, Recipe, Challenge, UserProfile, ForumCategory, ForumTopic, ForumPost, Notification, VIPPost, VIPComment, ContactMessage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'category', 'status', 'created_on')
    list_filter = ('status', 'category', 'created_on', 'is_featured')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_on'
    ordering = ('-created_on',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'calories', 'status', 'created_on')
    list_filter = ('status', 'created_on', 'is_featured')
    search_fields = ('title', 'ingredients', 'instructions', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_on'
    ordering = ('-created_on',)

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'duration', 'is_active', 'created_on')
    list_filter = ('is_active', 'created_on')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_weight', 'height', 'goal_weight', 'bmi', 'is_vip', 'vip_expires_at', 'vip_status')
    search_fields = ('user__username', 'user__email', 'bio')
    list_filter = ('is_vip',)
    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'profile_pic')
        }),
        ('Информация о весе', {
            'fields': ('starting_weight', 'current_weight', 'goal_weight', 'height')
        }),
        ('VIP статус', {
            'fields': ('is_vip', 'vip_expires_at'),
            'description': 'Управление VIP статусом пользователя. Если срок не указан, VIP статус будет бессрочным.'
        }),
    )
    
    def bmi(self, obj):
        return obj.bmi()
    bmi.short_description = 'ИМТ'
    
    def vip_status(self, obj):
        if not obj.is_vip:
            return "Нет VIP"
        if obj.vip_expires_at:
            from django.utils import timezone
            if obj.vip_expires_at > timezone.now():
                return f"До {obj.vip_expires_at.strftime('%d.%m.%Y')}"
            else:
                return "Истек"
        return "Бессрочный"
    vip_status.short_description = 'Статус VIP'

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'author', 'created_on', 'views', 'is_closed', 'is_pinned')
    list_filter = ('category', 'is_closed', 'is_pinned', 'created_on')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_on'

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'topic', 'created_on')
    list_filter = ('created_on', 'is_solution')
    search_fields = ('content', 'author__username', 'topic__title')
    raw_id_fields = ('author', 'topic', 'parent')
    date_hierarchy = 'created_on'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'sender', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'title', 'message')
    raw_id_fields = ('recipient', 'sender', 'content_type')
    date_hierarchy = 'created_at'
    list_editable = ('is_read',)
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} уведомлений отмечено как прочитанные.')
    
    mark_as_read.short_description = "Отметить выбранные уведомления как прочитанные"

@admin.register(VIPPost)
class VIPPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_on')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('created_on', 'author')
    
@admin.register(VIPComment)
class VIPCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_on')
    search_fields = ('content', 'author__username', 'post__title')
    list_filter = ('created_on', 'author')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'
    list_editable = ('is_read',)
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} сообщений отмечено как прочитанные.')
    
    mark_as_read.short_description = "Отметить выбранные сообщения как прочитанные"
