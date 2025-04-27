from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Post, ForumTopic, ForumPost, Category, Comment, Recipe, RecipeComment
from django.utils.text import slugify
import random
import string

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Обязательное поле")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'profile_pic', 'current_weight', 'height', 'goal_weight', 'starting_weight')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'current_weight': forms.NumberInput(attrs={'step': '0.1'}),
            'height': forms.NumberInput(attrs={'step': '0.1'}),
            'goal_weight': forms.NumberInput(attrs={'step': '0.1'}),
            'starting_weight': forms.NumberInput(attrs={'step': '0.1'}),
        }
        labels = {
            'bio': 'О себе',
            'profile_pic': 'Фото профиля',
            'current_weight': 'Текущий вес (кг)',
            'height': 'Рост (см)',
            'goal_weight': 'Целевой вес (кг)',
            'starting_weight': 'Начальный вес (кг)',
        }
        help_texts = {
            'bio': 'Расскажите немного о себе и своих целях',
            'height': 'Ваш рост в сантиметрах',
        }

# Формы для пользовательских статей
class UserPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'category', 'featured_image', 'content')
        labels = {
            'title': 'Заголовок',
            'category': 'Категория',
            'featured_image': 'Изображение',
            'content': 'Содержание статьи',
        }
        help_texts = {
            'title': 'Название вашей статьи',
            'category': 'Выберите категорию, к которой относится ваша статья',
            'featured_image': 'Загрузите изображение для статьи (необязательно)',
            'content': 'Содержание вашей статьи',
        }
    
    def save(self, commit=True, user=None):
        post = super().save(commit=False)
        post.status = 'draft'  # Все пользовательские статьи сначала в статусе черновика
        
        if user:
            post.author = user
        
        # Генерация уникального slug из заголовка
        base_slug = slugify(post.title)
        unique_slug = base_slug
        counter = 1
        
        while Post.objects.filter(slug=unique_slug).exists():
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            unique_slug = f"{base_slug}-{random_suffix}"
            counter += 1
        
        post.slug = unique_slug
        
        if commit:
            post.save()
        
        return post

# Формы для форума
class ForumTopicForm(forms.ModelForm):
    class Meta:
        model = ForumTopic
        fields = ('title', 'category', 'content')
        labels = {
            'title': 'Заголовок темы',
            'category': 'Раздел форума',
            'content': 'Сообщение',
        }
        help_texts = {
            'title': 'Заголовок должен отражать суть вашего вопроса',
            'category': 'Выберите подходящий раздел форума',
            'content': 'Опишите вашу проблему или вопрос подробно',
        }
    
    def save(self, commit=True, user=None):
        topic = super().save(commit=False)
        
        if user:
            topic.author = user
        
        # Генерация уникального slug
        base_slug = slugify(topic.title)
        unique_slug = base_slug
        counter = 1
        
        while ForumTopic.objects.filter(slug=unique_slug).exists():
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            unique_slug = f"{base_slug}-{random_suffix}"
            counter += 1
        
        topic.slug = unique_slug
        
        if commit:
            topic.save()
        
        # Создаем первый пост в теме
        if commit and user:
            first_post = ForumPost(
                topic=topic,
                author=user,
                content=topic.content,
            )
            first_post.save()
        
        return topic

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ('content',)
        labels = {
            'content': 'Ваш ответ',
        }
        
    def __init__(self, *args, **kwargs):
        self.parent_post = kwargs.pop('parent_post', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.parent_post:
            instance.parent = self.parent_post
        if commit:
            instance.save()
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        labels = {
            'content': 'Ваш комментарий',
        }
        
    def __init__(self, *args, **kwargs):
        self.parent_comment = kwargs.pop('parent_comment', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.parent_comment:
            instance.parent = self.parent_comment
        if commit:
            instance.save()
        return instance

class RecipeCommentForm(forms.ModelForm):
    class Meta:
        model = RecipeComment
        fields = ('content',)
        labels = {
            'content': 'Ваш комментарий',
        }
        
    def __init__(self, *args, **kwargs):
        self.parent_comment = kwargs.pop('parent_comment', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.parent_comment:
            instance.parent = self.parent_comment
        if commit:
            instance.save()
        return instance

class UserRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'calories', 'protein', 'carbs', 'fat', 'preparation_time', 'image', 'ingredients', 'instructions']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название рецепта'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 350'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество белка в граммах'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество углеводов в граммах'}),
            'fat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество жиров в граммах'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Время приготовления в минутах'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название рецепта',
            'calories': 'Калории',
            'protein': 'Белки (г)',
            'carbs': 'Углеводы (г)',
            'fat': 'Жиры (г)',
            'preparation_time': 'Время приготовления (мин)',
            'image': 'Фото блюда',
            'ingredients': 'Ингредиенты',
            'instructions': 'Инструкции по приготовлению',
        }
        help_texts = {
            'title': 'Выберите краткое, но информативное название',
            'image': 'Загрузите качественное фото готового блюда. Рекомендуемый размер: 800x600 пикселей',
            'ingredients': 'Перечислите все ингредиенты с указанием количества',
            'instructions': 'Подробно опишите процесс приготовления блюда шаг за шагом',
        } 