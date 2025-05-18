from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify
import random
import string
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .utils import generate_unique_slug

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])
    
    def published_count(self):
        return self.posts.filter(status='published').count()

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('pending', 'На модерации'),
        ('rejected', 'Отклонено'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    content = CKEditor5Field('Содержание', config_name='default')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_on']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Post, self.title)
        super().save(*args, **kwargs)
    
    def comment_count(self):
        return self.comments.count()
    
    def get_comments(self):
        return self.comments.filter(parent=None).order_by('-created_on')

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = CKEditor5Field('Содержание', config_name='default')
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_on']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    def get_replies(self):
        return Comment.objects.filter(parent=self).order_by('created_on')

class Recipe(models.Model):
    STATUS_CHOICES = (
        ('draft', 'На рассмотрении'),
        ('published', 'Опубликовано'),
        ('rejected', 'Отклонено'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', null=True, blank=True)
    image = models.ImageField(upload_to='recipes/')
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField(help_text='Белки в граммах')
    carbs = models.PositiveIntegerField(help_text='Углеводы в граммах')
    fat = models.PositiveIntegerField(help_text='Жиры в граммах')
    preparation_time = models.PositiveIntegerField(help_text='Время в минутах')
    ingredients = CKEditor5Field('Ингредиенты', config_name='default')
    instructions = CKEditor5Field('Инструкции', config_name='default')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    rejection_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('recipe_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Recipe, self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_on']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        
    def comment_count(self):
        return self.recipe_comments.count()
    
    def get_comments(self):
        return self.recipe_comments.filter(parent=None).order_by('-created_on')

class RecipeComment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = CKEditor5Field('Содержание', config_name='default')
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_on']
        verbose_name = 'Комментарий к рецепту'
        verbose_name_plural = 'Комментарии к рецептам'
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.recipe.title}'
    
    def get_replies(self):
        return RecipeComment.objects.filter(parent=self).order_by('created_on')

class Challenge(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = CKEditor5Field('Описание', config_name='default')
    image = models.ImageField(upload_to='challenges/', blank=True, null=True)
    duration = models.PositiveIntegerField(help_text='Продолжительность в днях')
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('challenge_detail', args=[self.slug])
    
    class Meta:
        ordering = ['-created_on']
        verbose_name = 'Челлендж'
        verbose_name_plural = 'Челленджи'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    starting_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    goal_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_vip = models.BooleanField(default=False, verbose_name="VIP статус")
    vip_expires_at = models.DateTimeField(blank=True, null=True, verbose_name="Срок действия VIP статуса")
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def get_absolute_url(self):
        return reverse('profile_detail', args=[self.user.username])
    
    def bmi(self):
        if self.current_weight and self.height:
            return round((self.current_weight / ((self.height / 100) ** 2)), 2)
        return None
    
    def weight_loss_progress(self):
        if self.current_weight and self.goal_weight and self.starting_weight:
            total_loss = float(self.starting_weight) - float(self.current_weight)
            total_goal = float(self.starting_weight) - float(self.goal_weight)
            if total_goal > 0:
                return round((total_loss / total_goal) * 100, 2)
        return 0
    
    def has_active_vip(self):
        """Проверяет, активен ли VIP-статус пользователя"""
        if not self.is_vip:
            return False
        if self.vip_expires_at is None:
            return True  # Бессрочный VIP
        return self.vip_expires_at > timezone.now()
        
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

# Новые модели для форума
class ForumCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome class e.g. 'fa-users'")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Forum Categories'
        ordering = ['order']
        verbose_name = 'Категория форума'
        verbose_name_plural = 'Категории форума'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('forum_category', args=[self.slug])
    
    def topics_count(self):
        return self.topics.count()
    
    def last_topic(self):
        return self.topics.order_by('-created_on').first()

class ForumTopic(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    content = CKEditor5Field('Содержание', config_name='default')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_on']
        verbose_name = 'Тема форума'
        verbose_name_plural = 'Темы форума'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forum_topic_detail', args=[self.category.slug, self.slug])
    
    def posts_count(self):
        return self.forum_posts.count()
    
    def replies_count(self):
        # Возвращает количество ответов (без учета начального поста)
        return self.forum_posts.count() - 1 if self.forum_posts.count() > 0 else 0
    
    def last_post(self):
        return self.forum_posts.order_by('-created_on').first()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ForumTopic, self.title)
        super().save(*args, **kwargs)

class ForumPost(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='forum_posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = CKEditor5Field('Содержание', config_name='default')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_solution = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_on']
        verbose_name = 'Сообщение форума'
        verbose_name_plural = 'Сообщения форума'
    
    def __str__(self):
        return f'Post by {self.author.username} on {self.topic.title}'
    
    def get_replies(self):
        return ForumPost.objects.filter(parent=self).order_by('created_on')
    
    def get_absolute_url(self):
        return f'{self.topic.get_absolute_url()}#post-{self.id}'
        
    def total_replies_count(self):
        """
        Рекурсивно подсчитывает общее количество ответов на этот пост,
        включая ответы на ответы на всех уровнях вложенности.
        """
        # Получаем прямые ответы
        direct_replies = self.get_replies().count()
        
        # Рекурсивно подсчитываем ответы на ответы
        nested_replies = 0
        for reply in self.get_replies():
            nested_replies += reply.total_replies_count()
            
        # Возвращаем сумму прямых и вложенных ответов
        return direct_replies + nested_replies

# Модель для уведомлений пользователя
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('comment', 'Комментарий'),
        ('reply', 'Ответ'),
        ('like', 'Лайк'),
        ('forum_reply', 'Ответ на форуме'),
        ('mention', 'Упоминание'),
        ('status_update', 'Обновление статуса'),
        ('weight_goal', 'Достижение цели по весу'),
        ('system', 'Системное уведомление'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    
    # Для связи с любой моделью (Post, Comment, ForumTopic и т.д.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    url = models.CharField(max_length=255, blank=True)  # URL для перехода при клике на уведомление
    is_read = models.BooleanField(default=False)  # Прочитано ли уведомление
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
    
    def __str__(self):
        return f"Уведомление для {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, 
                          sender=None, content_object=None, url=None):
        """
        Создает новое уведомление
        """
        notification = cls(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            url=url
        )
        
        if content_object:
            notification.content_object = content_object
            
        notification.save()
        return notification

# VIP раздел
class VIPPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = CKEditor5Field('Содержание', config_name='default')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vip_posts')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_on']
        verbose_name = "VIP статья"
        verbose_name_plural = "VIP статьи"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('vip_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(VIPPost, self.title)
        super().save(*args, **kwargs)

class VIPComment(models.Model):
    post = models.ForeignKey(VIPPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vip_comments')
    content = CKEditor5Field('Содержание', config_name='default')
    created_on = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_on']
        verbose_name = "VIP комментарий"
        verbose_name_plural = "VIP комментарии"
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Сообщение обратной связи"
        verbose_name_plural = "Сообщения обратной связи"
    
    def __str__(self):
        return f'Сообщение от {self.name}: {self.subject}'

# Модели для калькулятора рациона и плана питания
class FoodCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome класс, напр. 'fa-apple'")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Категория продуктов"
        verbose_name_plural = "Категории продуктов"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(FoodCategory, self.name)
        super().save(*args, **kwargs)

class Food(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название продукта")
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name="foods", verbose_name="Категория")
    calories = models.PositiveIntegerField(verbose_name="Калории на 100г")
    protein = models.FloatField(verbose_name="Белки на 100г (г)")
    fats = models.FloatField(verbose_name="Жиры на 100г (г)")
    carbs = models.FloatField(verbose_name="Углеводы на 100г (г)")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="custom_foods", verbose_name="Пользователь")
    is_custom = models.BooleanField(default=False, verbose_name="Пользовательский продукт")
    image = models.ImageField(upload_to='foods/', null=True, blank=True, verbose_name="Изображение")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
    
    def __str__(self):
        return self.name

class NutritionGoal(models.Model):
    GOAL_CHOICES = (
        ('maintain', 'Поддерживать вес'),
        ('lose_slow', 'Медленное похудение (-10%)'),
        ('lose_medium', 'Среднее похудение (-15%)'),
        ('lose_fast', 'Быстрое похудение (-20%)'),
        ('gain_slow', 'Медленный набор (+10%)'),
        ('gain_medium', 'Средний набор (+15%)'),
        ('gain_fast', 'Быстрый набор (+20%)'),
    )
    
    ACTIVITY_CHOICES = (
        ('sedentary', 'Сидячий образ жизни'),
        ('light', 'Тренировки 1-3 раза в неделю'),
        ('moderate', 'Тренировки 3-5 раз в неделю'),
        ('active', 'Тренировки 6-7 раз в неделю'),
        ('very_active', 'Тяжелая физическая работа или 2 тренировки в день'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Мужчина'),
        ('female', 'Женщина'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nutrition_goals", verbose_name="Пользователь")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Пол")
    age = models.PositiveIntegerField(verbose_name="Возраст")
    height = models.PositiveIntegerField(verbose_name="Рост (см)")
    weight = models.FloatField(verbose_name="Вес (кг)")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, verbose_name="Уровень активности")
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, verbose_name="Цель")
    
    # Рассчитанные значения
    base_calories = models.PositiveIntegerField(verbose_name="Базовые калории")
    target_calories = models.PositiveIntegerField(verbose_name="Целевые калории")
    protein_per_kg = models.FloatField(verbose_name="Белки на кг веса")
    protein_daily = models.FloatField(verbose_name="Белки в день (г)")
    fats_per_kg = models.FloatField(verbose_name="Жиры на кг веса")
    fats_daily = models.FloatField(verbose_name="Жиры в день (г)")
    carbs_daily = models.FloatField(verbose_name="Углеводы в день (г)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Цель по питанию"
        verbose_name_plural = "Цели по питанию"
    
    def __str__(self):
        return f"План питания {self.user.username}: {self.get_goal_display()}"
    
    def save(self, *args, **kwargs):
        # Расчет базовых калорий на основе формулы Миффлина-Сент Жеора
        if self.gender == 'male':
            self.base_calories = int((10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5)
        else:
            self.base_calories = int((10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161)
        
        # Коэффициент активности
        activity_multiplier = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }[self.activity_level]
        
        # Коррекция по цели
        goal_modifier = {
            'maintain': 1.0,
            'lose_slow': 0.9,
            'lose_medium': 0.85,
            'lose_fast': 0.8,
            'gain_slow': 1.1,
            'gain_medium': 1.15,
            'gain_fast': 1.2,
        }[self.goal]
        
        self.target_calories = int(self.base_calories * activity_multiplier * goal_modifier)
        
        # Расчет макронутриентов
        # Белок: при похудении - больше, при наборе - меньше
        if 'lose' in self.goal:
            self.protein_per_kg = 1.8  # 1.8г белка на кг при похудении
        elif 'gain' in self.goal:
            self.protein_per_kg = 2.0  # 2.0г белка на кг при наборе массы
        else:
            self.protein_per_kg = 1.6  # 1.6г белка на кг при поддержании
        
        self.protein_daily = round(self.protein_per_kg * self.weight, 1)
        
        # Жиры: минимум 0.8г на кг веса
        self.fats_per_kg = 0.9
        self.fats_daily = round(self.fats_per_kg * self.weight, 1)
        
        # Углеводы: оставшиеся калории
        protein_calories = self.protein_daily * 4  # 4 ккал на 1г белка
        fat_calories = self.fats_daily * 9  # 9 ккал на 1г жира
        carbs_calories = self.target_calories - protein_calories - fat_calories
        self.carbs_daily = round(carbs_calories / 4, 1)  # 4 ккал на 1г углеводов
        
        super().save(*args, **kwargs)

class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans", verbose_name="Пользователь")
    name = models.CharField(max_length=200, verbose_name="Название плана")
    nutrition_goal = models.ForeignKey(NutritionGoal, on_delete=models.CASCADE, related_name="meal_plans", verbose_name="Цель по питанию")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "План питания"
        verbose_name_plural = "Планы питания"
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def total_calories(self):
        """Возвращает общее количество калорий в плане питания"""
        total = 0
        for meal in self.meals.all():
            total += meal.total_calories()
        return total
    
    def total_protein(self):
        """Возвращает общее количество белка в плане питания"""
        total = 0
        for meal in self.meals.all():
            total += meal.total_protein()
        return total
    
    def total_fats(self):
        """Возвращает общее количество жиров в плане питания"""
        total = 0
        for meal in self.meals.all():
            total += meal.total_fats()
        return total
    
    def total_carbs(self):
        """Возвращает общее количество углеводов в плане питания"""
        total = 0
        for meal in self.meals.all():
            total += meal.total_carbs()
        return total

class Meal(models.Model):
    MEAL_TYPE_CHOICES = (
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('snack', 'Перекус'),
    )
    
    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="meals", verbose_name="План питания")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, verbose_name="Тип приема пищи")
    day_of_week = models.PositiveIntegerField(choices=[(i, d) for i, d in enumerate(['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'], 1)], verbose_name="День недели")
    
    class Meta:
        ordering = ['day_of_week', 'meal_type']
        verbose_name = "Прием пищи"
        verbose_name_plural = "Приемы пищи"
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.get_meal_type_display()}"
    
    def total_calories(self):
        """Возвращает общее количество калорий в приеме пищи"""
        total = 0
        for item in self.meal_items.all():
            total += item.calories
        return total
    
    def total_protein(self):
        """Возвращает общее количество белка в приеме пищи"""
        total = 0
        for item in self.meal_items.all():
            total += item.protein
        return total
    
    def total_fats(self):
        """Возвращает общее количество жиров в приеме пищи"""
        total = 0
        for item in self.meal_items.all():
            total += item.fats
        return total
    
    def total_carbs(self):
        """Возвращает общее количество углеводов в приеме пищи"""
        total = 0
        for item in self.meal_items.all():
            total += item.carbs
        return total

class MealItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="meal_items", verbose_name="Прием пищи")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="meal_items", verbose_name="Продукт")
    amount = models.PositiveIntegerField(verbose_name="Количество (г)")
    
    # Рассчитываемые поля
    calories = models.PositiveIntegerField(verbose_name="Калории", editable=False)
    protein = models.FloatField(verbose_name="Белки (г)", editable=False)
    fats = models.FloatField(verbose_name="Жиры (г)", editable=False)
    carbs = models.FloatField(verbose_name="Углеводы (г)", editable=False)
    
    class Meta:
        verbose_name = "Продукт в рационе"
        verbose_name_plural = "Продукты в рационе"
    
    def __str__(self):
        return f"{self.food.name} ({self.amount}г)"
    
    def save(self, *args, **kwargs):
        # Рассчитываем питательную ценность на основе количества
        self.calories = int(self.food.calories * self.amount / 100)
        self.protein = round(self.food.protein * self.amount / 100, 1)
        self.fats = round(self.food.fats * self.amount / 100, 1)
        self.carbs = round(self.food.carbs * self.amount / 100, 1)
        super().save(*args, **kwargs)
