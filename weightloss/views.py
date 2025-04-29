from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView, FormView, View
from .models import Category, Post, Recipe, Challenge, UserProfile, ForumCategory, ForumTopic, ForumPost, Comment, RecipeComment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.db.models import Q, Count, Max, F
from .forms import CustomUserCreationForm as UserRegisterForm, UserProfileForm, UserPostForm, ForumTopicForm, ForumPostForm, CommentForm, UserRecipeForm, RecipeCommentForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import random
import string
from django.http import Http404
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_ratelimit.decorators import ratelimit
from django.template.loader import render_to_string
import time
from unidecode import unidecode

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'weightloss/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(is_featured=True, status='published')[:3]
        context['featured_recipes'] = Recipe.objects.filter(status='published').order_by('-created_on')[:3]
        context['challenges'] = Challenge.objects.filter(is_active=True)[:2]
        return context

class BlogListView(ListView):
    model = Post
    template_name = 'weightloss/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9  # Показывать 9 постов на странице
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        
        # Фильтр по автору, если указан
        author_username = self.request.GET.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
            
        print(f"DEBUG - BlogListView get_queryset: found {queryset.count()} posts with status='published'")
        if queryset.count() > 0:
            for post in queryset:
                print(f"DEBUG - Post '{post.title}' has status '{post.status}' and category '{post.category.name}'")
        else:
            print("DEBUG - No published posts found!")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        
        # Add count of published posts for each category
        for category in categories:
            category.published_count = Post.objects.filter(category=category, status='published').count()
            
        context['categories'] = categories
        print(f"DEBUG - BlogListView context: posts={len(context.get('posts', []))}, categories={len(categories)}")
        return context

class BlogDetailView(DetailView):
    model = Post
    template_name = 'weightloss/blog_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        categories = Category.objects.all()
        related_posts = Post.objects.filter(status='published', category=post.category).exclude(id=post.id)[:3]
        
        # Get comments for this post - только комментарии верхнего уровня
        comments = Comment.objects.filter(post=post, parent=None).select_related('author')
        
        # Используем префетч для оптимизации загрузки ответов
        comments = comments.prefetch_related('replies', 'replies__author')
        
        # Подсчет общего количества комментариев, включая вложенные ответы
        total_comments = comments.count()
        for comment in comments:
            # Добавляем количество непосредственных ответов
            replies = comment.replies.all()
            total_comments += replies.count()
            
            # Добавляем количество вложенных ответов на ответы (глубокая вложенность)
            for reply in replies:
                total_comments += reply.replies.count()
                for nested_reply in reply.replies.all():
                    total_comments += nested_reply.replies.count()
        
        # Для каждого комментария подсчитываем все его ответы с учетом вложенных
        for comment in comments:
            comment.total_replies_count = comment.replies.count()
            for reply in comment.replies.all():
                comment.total_replies_count += reply.replies.count()
                for nested_reply in reply.replies.all():
                    comment.total_replies_count += nested_reply.replies.count()
        
        # Add comment form for authenticated users
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            
        context.update({
            'categories': categories,
            'related_posts': related_posts,
            'comments': comments,
            'total_comments': total_comments,
        })
        return context
        
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Ваш комментарий успешно добавлен.')
                return redirect(post.get_absolute_url() + '#comment-' + str(comment.id))
            else:
                messages.error(request, 'Произошла ошибка. Пожалуйста, проверьте введенные данные.')
        return redirect(post.get_absolute_url())

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'weightloss/category_detail.html'
    context_object_name = 'category'
    paginate_by = 9  # Same as BlogListView
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get posts for this category
        posts_list = Post.objects.filter(category=category, status='published')
        
        # Add pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(posts_list, self.paginate_by)
        
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        # Add to context
        context['posts'] = posts
        context['page_obj'] = posts  # For pagination template compatibility
        context['is_paginated'] = True if paginator.num_pages > 1 else False
        context['paginator'] = paginator
        
        # Add all categories for the sidebar
        context['categories'] = Category.objects.all()
        
        return context

class RecipeListView(ListView):
    model = Recipe
    template_name = 'weightloss/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 9  # Показывать 9 рецептов на странице
    
    def get_queryset(self):
        queryset = Recipe.objects.filter(status='published')
        
        # Фильтр по автору, если указан
        author_username = self.request.GET.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем информацию о выбранном авторе, если есть
        author_username = self.request.GET.get('author')
        if author_username:
            try:
                author = User.objects.get(username=author_username)
                context['filtered_author'] = author
            except User.DoesNotExist:
                pass
                
        return context

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'weightloss/recipe_detail.html'
    context_object_name = 'recipe'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = context['recipe']
        related_recipes = Recipe.objects.exclude(id=recipe.id).order_by('?')[:3]
        
        # Get comments for this recipe - only top-level comments
        comments = RecipeComment.objects.filter(recipe=recipe, parent=None).select_related('author')
        
        # Use prefetch for optimizing loading of replies
        comments = comments.prefetch_related('replies', 'replies__author')
        
        # Add comment form for authenticated users
        if self.request.user.is_authenticated:
            context['comment_form'] = RecipeCommentForm()
            
        context.update({
            'related_recipes': related_recipes,
            'comments': comments,
        })
        return context
        
    def post(self, request, *args, **kwargs):
        recipe = self.get_object()
        if request.user.is_authenticated:
            form = RecipeCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.recipe = recipe
                comment.author = request.user
                comment.save()
                messages.success(request, 'Ваш комментарий успешно добавлен.')
                return redirect(recipe.get_absolute_url() + '#comment-' + str(comment.id))
            else:
                messages.error(request, 'Произошла ошибка. Пожалуйста, проверьте введенные данные.')
        return redirect(recipe.get_absolute_url())

class ChallengeListView(ListView):
    model = Challenge
    template_name = 'weightloss/challenge_list.html'
    context_object_name = 'challenges'
    paginate_by = 6  # Показывать 6 челленджей на странице
    
    def get_queryset(self):
        return Challenge.objects.filter(is_active=True)

class ChallengeDetailView(DetailView):
    model = Challenge
    template_name = 'weightloss/challenge_detail.html'
    context_object_name = 'challenge'

class CalculatorView(TemplateView):
    template_name = 'weightloss/calculators.html'

class AboutView(TemplateView):
    template_name = 'weightloss/about.html'

class ContactView(TemplateView):
    template_name = 'weightloss/contact.html'

class SearchResultsView(ListView):
    template_name = 'weightloss/search_results.html'
    context_object_name = 'results'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            post_results = Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                status='published'
            )
            return post_results
        return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        if query:
            # The posts are already paginated via ListView
            post_results = context['page_obj'].object_list
            
            # Recipe results - no pagination needed as they're displayed separately
            recipe_results = Recipe.objects.filter(
                Q(title__icontains=query) | Q(ingredients__icontains=query) | Q(instructions__icontains=query),
                status='published'
            )
            
            context['results'] = {
                'posts': post_results,
                'recipes': recipe_results,
                'query': query,
                'total_posts': self.get_queryset().count(),
                'total_recipes': recipe_results.count()
            }
        else:
            context['results'] = {'posts': [], 'recipes': [], 'query': '', 'total_posts': 0, 'total_recipes': 0}
        return context

# Авторизация и регистрация

class CustomLoginView(LoginView):
    template_name = 'weightloss/auth/login.html'
    
    def get_success_url(self):
        return reverse_lazy('profile')

class CustomLogoutView(LogoutView):
    next_page = 'home'

class RegisterView(FormView):
    template_name = 'weightloss/auth/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.save()
        UserProfile.objects.create(user=user)
        login(self.request, user)
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'weightloss/auth/password_reset.html'
    email_template_name = 'weightloss/auth/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'weightloss/auth/password_reset_done.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'weightloss/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=self.request.user)
        
        context['profile'] = profile
        context['bmi'] = profile.bmi()
        context['user_posts'] = Post.objects.filter(author=self.request.user).order_by('-created_on')[:5]
        return context

class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'weightloss/public_profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        user = profile.user
        
        # Получаем публичную информацию о пользователе
        context['user_posts'] = Post.objects.filter(author=user, status='published').order_by('-created_on')[:5]
        context['user_recipes'] = Recipe.objects.filter(author=user, status='published').order_by('-created_on')[:5]
        context['forum_topics'] = ForumTopic.objects.filter(author=user).order_by('-created_on')[:5]
        context['bmi'] = profile.bmi()
        
        # Подсчитываем активность пользователя
        context['posts_count'] = Post.objects.filter(author=user, status='published').count()
        context['recipes_count'] = Recipe.objects.filter(author=user, status='published').count()
        context['forum_posts_count'] = ForumPost.objects.filter(author=user).count()
        context['comments_count'] = Comment.objects.filter(author=user).count() + RecipeComment.objects.filter(author=user).count()
        
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'weightloss/auth/edit_profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        try:
            return UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Профиль успешно обновлен!')
        return response

# Представления для пользовательских статей
class UserPostsListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'weightloss/blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10  # Показывать 10 постов на странице
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-created_on')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_posts = self.get_queryset()
        
        # Add filtered posts by status
        context['published_posts'] = user_posts.filter(status='published')
        context['pending_posts'] = user_posts.filter(status='pending')
        context['draft_posts'] = user_posts.filter(status='draft')
        context['rejected_posts'] = user_posts.filter(status='rejected')
        
        return context

class UserPostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = UserPostForm
    template_name = 'weightloss/user_post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_user_submitted = True
        form.instance.status = 'pending'  # Устанавливаем статус "на модерации"
        
        # Создаем уникальный slug
        title = form.instance.title.strip()
        base_slug = slugify(title)
        if not base_slug:
            # Если slugify вернул пустую строку (например, для кириллицы)
            # Транслитерация кириллицы на латиницу (примитивная)
            try:
                # Попытка использовать unidecode если он доступен
                transliterated = unidecode(title)
                base_slug = slugify(transliterated)
            except ImportError:
                # Если модуля нет, используем простой вариант со случайной строкой
                import random
                import string
                random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                base_slug = f"post-{random_string}"
            
            # Если всё ещё пустой slug, используем timestamp
            if not base_slug:
                import time
                base_slug = f"post-{int(time.time())}"
        
        unique_slug = base_slug
        counter = 1
        
        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        
        form.instance.slug = unique_slug
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('user_posts')

class UserPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = UserPostForm
    template_name = 'weightloss/user_post_form.html'
    
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user
    
    def form_valid(self, form):
        # Если пост был опубликован или отклонен, и пользователь его редактирует,
        # его следует вернуть на модерацию
        post = self.get_object()
        if post.status in ['published', 'rejected']:
            form.instance.status = 'pending'
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('user_posts')

# Представления для форума
class ForumHomeView(ListView):
    model = ForumCategory
    template_name = 'weightloss/forum/forum_home.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ForumCategory.objects.annotate(
            topics_count=Count('topics'),
            posts_count=Count('topics__forum_posts'),
            last_post_date=Max('topics__forum_posts__created_on')
        ).order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика форума
        context['topic_count'] = ForumTopic.objects.count()
        context['reply_count'] = ForumPost.objects.count()
        context['member_count'] = User.objects.count()
        
        # Последний зарегистрированный пользователь
        try:
            context['latest_member'] = User.objects.latest('date_joined')
        except User.DoesNotExist:
            context['latest_member'] = None
            
        return context

class ForumCategoryView(DetailView):
    model = ForumCategory
    template_name = 'weightloss/forum/forum_category.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Сортируем темы
        topics_list = ForumTopic.objects.filter(category=category).annotate(
            last_post_date=Max('forum_posts__created_on')
        ).select_related('author').order_by('-is_pinned', '-updated_on')
        
        # Добавляем пагинацию
        page = self.request.GET.get('page', 1)
        paginator = Paginator(topics_list, 10)  # Показывать 10 тем на странице
        
        try:
            topics = paginator.page(page)
        except PageNotAnInteger:
            topics = paginator.page(1)
        except EmptyPage:
            topics = paginator.page(paginator.num_pages)
        
        context['topics'] = topics
        context['page_obj'] = topics  # Для совместимости с шаблоном пагинации
        return context

class ForumTopicDetailView(DetailView):
    model = ForumTopic
    template_name = 'weightloss/forum/forum_topic_detail.html'
    context_object_name = 'topic'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        category_slug = self.kwargs.get('category_slug')
        topic_slug = self.kwargs.get('slug')
        topic = get_object_or_404(ForumTopic, slug=topic_slug, category__slug=category_slug)
        if not self.request.session.get(f'topic_viewed_{topic.id}'):
            topic.views += 1
            topic.save()
            self.request.session[f'topic_viewed_{topic.id}'] = True
        return topic
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        
        # Получаем все посты темы верхнего уровня
        posts_list = ForumPost.objects.filter(topic=topic, parent=None).select_related('author')
        
        # Используем префетч для оптимизации загрузки ответов
        posts_list = posts_list.prefetch_related('replies', 'replies__author', 'replies__replies', 'replies__replies__replies')
        
        # Для каждого поста подсчитываем все его ответы с учетом вложенных
        for post in posts_list:
            # Улучшенный рекурсивный подсчет всех вложенных ответов
            post.total_replies_count = self._count_nested_replies(post)
        
        # Добавляем пагинацию
        page = self.request.GET.get('page', 1)
        paginator = Paginator(posts_list, 10)  # Показывать 10 постов на странице
        
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['posts'] = posts
        context['total_posts_count'] = posts_list.count()  # Добавляем общее количество постов
        context['form'] = ForumPostForm()
        
        # Добавляем все категории форума для отображения в боковой панели
        context['forum_categories'] = ForumCategory.objects.all().order_by('order')
        
        return context
    
    def _count_nested_replies(self, post):
        """
        Рекурсивно подсчитывает все вложенные ответы для поста.
        """
        total = post.replies.count()
        
        # Рекурсивно обрабатываем все ответы
        for reply in post.replies.all():
            total += self._count_nested_replies(reply)
            
        return total

class ForumTopicCreateView(LoginRequiredMixin, CreateView):
    model = ForumTopic
    form_class = ForumTopicForm
    template_name = 'weightloss/forum/forum_topic_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        
        # Если передана категория в URL
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(ForumCategory, slug=category_slug)
            form.instance.category = category
        
        # Создаем уникальный slug
        title = form.instance.title.strip()
        base_slug = slugify(title)
        
        # Для случаев с кириллицей или когда slugify вернул пустую строку
        if not base_slug:
            # Транслитерация (примитивная) кириллицы или создание случайного slug
            import random
            import string
            
            # Создаем случайный суффикс
            random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            
            # Используем первые 20 символов названия (заменяя пробелы на дефисы)
            safe_title = title[:20].replace(' ', '-').lower() if title else ''
            
            # Если есть безопасные символы в названии, используем их + случайный суффикс
            # иначе просто случайный topic-id
            if safe_title:
                base_slug = f"{safe_title}-{random_string}"
            else:
                base_slug = f"topic-{random_string}"
        
        # Убеждаемся в уникальности slug
        unique_slug = base_slug
        counter = 1
        
        while ForumTopic.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Проверяем не пустой ли slug (для безопасности)
        if not unique_slug:
            unique_slug = f"topic-{random.randint(10000, 99999)}"
            
        form.instance.slug = unique_slug
        
        # Save the form to create the topic
        self.object = form.save()
        
        # Создаем первый пост темы
        ForumPost.objects.create(
            topic=self.object,
            author=self.request.user,
            content=form.cleaned_data['content']
        )
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['category'] = get_object_or_404(ForumCategory, slug=category_slug)
        return context
    
    def get_success_url(self):
        return self.object.get_absolute_url()

class ForumPostCreateView(LoginRequiredMixin, CreateView):
    model = ForumPost
    form_class = ForumPostForm
    template_name = 'weightloss/forum/forum_post_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # Check if this is a reply to another post
        parent_id = self.request.GET.get('reply_to')
        if parent_id:
            try:
                parent_post = ForumPost.objects.get(id=parent_id)
                kwargs['parent_post'] = parent_post
            except ForumPost.DoesNotExist:
                pass
                
        return kwargs
    
    def form_valid(self, form):
        topic = get_object_or_404(
            ForumTopic, 
            slug=self.kwargs.get('topic_slug'),
            category__slug=self.kwargs.get('category_slug')
        )
        
        if topic.is_closed:
            return HttpResponseRedirect(topic.get_absolute_url())
        
        form.instance.topic = topic
        form.instance.author = self.request.user
        
        # Set parent post if this is a reply
        parent_id = self.request.GET.get('reply_to')
        if parent_id:
            try:
                parent_post = ForumPost.objects.get(id=parent_id)
                form.instance.parent = parent_post
            except ForumPost.DoesNotExist:
                pass
        
        # Обновляем дату последнего обновления темы
        topic.updated_on = timezone.now()
        topic.save()
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = get_object_or_404(
            ForumTopic, 
            slug=self.kwargs.get('topic_slug'),
            category__slug=self.kwargs.get('category_slug')
        )
        context['topic'] = topic
        
        # Add parent post to context if replying
        parent_id = self.request.GET.get('reply_to')
        if parent_id:
            try:
                context['parent_post'] = ForumPost.objects.get(id=parent_id)
            except ForumPost.DoesNotExist:
                pass
                
        return context
    
    def get_success_url(self):
        return self.object.get_absolute_url()

class CommentReplyView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'weightloss/blog/comment_reply_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        parent_id = self.kwargs.get('comment_id')
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
                kwargs['parent_comment'] = parent_comment
            except Comment.DoesNotExist:
                raise Http404("Комментарий не найден")
        return kwargs
    
    def form_valid(self, form):
        parent_id = self.kwargs.get('comment_id')
        post_slug = self.kwargs.get('slug')
        
        try:
            post = Post.objects.get(slug=post_slug)
            parent_comment = Comment.objects.get(id=parent_id)
            
            # Добавляем отладку
            is_nested = parent_comment.parent is not None
            parent_of_parent_id = parent_comment.parent.id if is_nested else None
            print(f"Creating reply to comment {parent_id}")
            print(f"Is this a reply to a reply? {is_nested}")
            if is_nested:
                print(f"Original parent comment ID: {parent_of_parent_id}")
            
            # Убираем ограничение на глубину вложенности - теперь комментарии могут быть любой глубины
            # Это убрано, так как мы поддерживаем любой уровень вложенности в шаблоне
            """
            if is_nested:
                # We're replying to a reply already
                # Find the original parent of this reply
                original_parent = parent_comment.parent
                
                # If the original parent already has a parent (i.e., it's a 3rd level reply)
                # we want to keep our comment as a 2nd level reply attached to the top level comment
                if original_parent.parent is not None:
                    print(f"Limiting nesting depth - attaching to original parent {original_parent.parent.id}")
                    parent_comment = original_parent.parent
                else:
                    print(f"Setting parent to original parent {original_parent.id}")
                    parent_comment = original_parent
            """
            
        except (Post.DoesNotExist, Comment.DoesNotExist):
            raise Http404("Пост или комментарий не найден")
        
        form.instance.post = post
        form.instance.author = self.request.user
        form.instance.parent = parent_comment  # Устанавливаем родительский комментарий
        self.object = form.save()
        
        # Еще отладка после сохранения
        print(f"Created comment {self.object.id} with parent {self.object.parent.id}")
        
        messages.success(self.request, 'Ваш ответ успешно добавлен.')
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_id = self.kwargs.get('comment_id')
        post_slug = self.kwargs.get('slug')
        
        try:
            context['post'] = Post.objects.get(slug=post_slug)
            context['parent_comment'] = Comment.objects.get(id=parent_id)
        except (Post.DoesNotExist, Comment.DoesNotExist):
            raise Http404("Пост или комментарий не найден")
            
        return context
    
    def get_success_url(self):
        return self.object.post.get_absolute_url() + '#comment-' + str(self.object.id)

# Представления для пользовательских рецептов
class UserRecipesListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'weightloss/recipe/user_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 10  # Показывать 10 рецептов на странице
    
    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by('-created_on')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipes = self.get_queryset()
        
        # Подсчет количества рецептов с разными статусами
        context['pending_count'] = recipes.filter(status='pending').count()
        context['published_count'] = recipes.filter(status='published').count()
        context['rejected_count'] = recipes.filter(status='rejected').count()
        context['draft_count'] = recipes.filter(status='draft').count()
        
        return context

class UserRecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = UserRecipeForm
    template_name = 'weightloss/recipe/user_recipe_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_user_submitted = True
        form.instance.status = 'pending'  # Устанавливаем статус "на модерации"
        
        # Slug будет создан автоматически в методе save() модели
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Ваш рецепт отправлен на модерацию и будет опубликован после проверки.')
        return reverse('user_recipes')

class UserRecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    form_class = UserRecipeForm
    template_name = 'weightloss/recipe/user_recipe_form.html'
    
    def test_func(self):
        recipe = self.get_object()
        return recipe.author == self.request.user
    
    def form_valid(self, form):
        # Если рецепт был опубликован или отклонен, и пользователь его редактирует,
        # его следует вернуть на модерацию
        recipe = self.get_object()
        if recipe.status in ['published', 'rejected']:
            form.instance.status = 'pending'
        
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Ваш рецепт успешно обновлен и отправлен на повторную модерацию.')
        return reverse('user_recipes')

class UserRecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    template_name = 'weightloss/recipe/user_recipe_confirm_delete.html'
    success_url = reverse_lazy('user_recipes')
    
    def test_func(self):
        recipe = self.get_object()
        return recipe.author == self.request.user

# Административные представления для рецептов (только для персонала)
class AdminRecipeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Recipe
    template_name = 'weightloss/recipe/admin_recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 15  # Показывать 15 рецептов на странице
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        status = self.request.GET.get('status', 'pending')
        return Recipe.objects.filter(status=status).order_by('-created_on')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', 'pending')
        
        # Подсчет количества рецептов с разными статусами
        context['pending_count'] = Recipe.objects.filter(status='pending').count()
        context['published_count'] = Recipe.objects.filter(status='published').count()
        context['rejected_count'] = Recipe.objects.filter(status='rejected').count()
        
        return context

class AdminRecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    template_name = 'weightloss/recipe/admin_recipe_form.html'
    fields = ['title', 'calories', 'protein', 'carbs', 'fat', 'preparation_time', 'image', 'ingredients', 'instructions', 'status', 'is_featured']
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, f'Рецепт "{self.object.title}" успешно обновлен.')
        return reverse('admin_recipe_list') + f'?status={self.object.status}'

class ForumSearchView(ListView):
    template_name = 'weightloss/forum/forum_search.html'
    context_object_name = 'topics'
    paginate_by = 10  # Показывать 10 результатов на странице
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            # Поиск по названию темы или содержанию постов
            topics = ForumTopic.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(forum_posts__content__icontains=query)
            ).distinct()
            return topics
        return ForumTopic.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class RecipeCommentReplyView(LoginRequiredMixin, CreateView):
    model = RecipeComment
    form_class = RecipeCommentForm
    template_name = 'weightloss/recipe/recipe_comment_reply_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        parent_id = self.kwargs.get('comment_id')
        if parent_id:
            try:
                parent_comment = RecipeComment.objects.get(id=parent_id)
                kwargs['parent_comment'] = parent_comment
            except RecipeComment.DoesNotExist:
                raise Http404("Комментарий не найден")
        return kwargs
    
    def form_valid(self, form):
        parent_id = self.kwargs.get('comment_id')
        recipe_slug = self.kwargs.get('slug')
        
        try:
            recipe = Recipe.objects.get(slug=recipe_slug)
            parent_comment = RecipeComment.objects.get(id=parent_id)
            
            # Add debugging
            is_nested = parent_comment.parent is not None
            parent_of_parent_id = parent_comment.parent.id if is_nested else None
            
            print(f"Creating reply to recipe comment {parent_id}")
            print(f"Is this a reply to a reply? {is_nested}")
            if is_nested:
                print(f"Original parent comment ID: {parent_of_parent_id}")
            
            # Убираем ограничение на глубину вложенности - поддерживаем любой уровень вложенности
            """
            # Fix for deeply nested comments - find the original top-level parent
            # only go 2 levels deep at most (replies to replies)
            if is_nested:
                # We're replying to a reply already
                # Find the original parent of this reply
                original_parent = parent_comment.parent
                
                # If the original parent already has a parent (i.e., it's a 3rd level reply)
                # we want to keep our comment as a 2nd level reply attached to the top level comment
                if original_parent.parent is not None:
                    print(f"Limiting nesting depth - attaching to original parent {original_parent.parent.id}")
                    parent_comment = original_parent.parent
                else:
                    print(f"Setting parent to original parent {original_parent.id}")
                    parent_comment = original_parent
            """
                
        except (Recipe.DoesNotExist, RecipeComment.DoesNotExist):
            raise Http404("Рецепт или комментарий не найден")
        
        form.instance.recipe = recipe
        form.instance.author = self.request.user
        form.instance.parent = parent_comment
        self.object = form.save()
        
        # More debugging after saving
        print(f"Created comment {self.object.id} with parent {self.object.parent.id}")
        
        messages.success(self.request, 'Ваш ответ успешно добавлен.')
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_id = self.kwargs.get('comment_id')
        recipe_slug = self.kwargs.get('slug')
        
        try:
            context['recipe'] = Recipe.objects.get(slug=recipe_slug)
            context['parent_comment'] = RecipeComment.objects.get(id=parent_id)
        except (Recipe.DoesNotExist, RecipeComment.DoesNotExist):
            raise Http404("Рецепт или комментарий не найден")
            
        return context
    
    def get_success_url(self):
        return self.object.recipe.get_absolute_url() + '#comment-' + str(self.object.id)

# Юридические страницы
class PrivacyPolicyView(TemplateView):
    template_name = 'weightloss/legal/privacy_policy.html'

class TermsOfServiceView(TemplateView):
    template_name = 'weightloss/legal/terms_of_service.html'

class CookiePolicyView(TemplateView):
    template_name = 'weightloss/legal/cookie_policy.html'

# SEO представления
class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'

# Временное представление для отладки проблемы блога
class TestBlogView(TemplateView):
    template_name = 'weightloss/test_blog.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_posts = Post.objects.all()
        published_posts = Post.objects.filter(status='published')
        
        context['all_posts'] = all_posts
        context['published_posts'] = published_posts
        context['debug_mode'] = True
        
        return context
        
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        # Если запрошен ответ JSON
        if request.GET.get('format') == 'json':
            from django.http import JsonResponse
            
            posts_data = []
            for post in context['published_posts']:
                posts_data.append({
                    'id': post.id,
                    'title': post.title,
                    'slug': post.slug,
                    'status': post.status,
                    'category': post.category.name,
                    'author': post.author.username,
                    'created': str(post.created_on),
                })
            
            return JsonResponse({
                'total_posts': context['all_posts'].count(),
                'published_posts': context['published_posts'].count(),
                'posts': posts_data
            })
        
        return super().get(request, *args, **kwargs)

class ForumPostReplyView(LoginRequiredMixin, View):
    """
    Обработка AJAX-запросов на добавление ответов к постам в форуме
    """
    def post(self, request, post_id):
        print(f"ForumPostReplyView: получен запрос на ответ к посту {post_id}")
        print(f"POST данные: {request.POST}")
        
        try:
            parent_post = get_object_or_404(ForumPost, id=post_id)
            topic = parent_post.topic
            
            if topic.is_closed:
                print(f"Ошибка: тема {topic.id} закрыта для новых ответов")
                return JsonResponse({
                    'status': 'error',
                    'message': 'This topic is closed for new replies.'
                }, status=403)
            
            content = request.POST.get('content', '').strip()
            if not content:
                print("Ошибка: содержимое ответа пустое")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Reply content cannot be empty.'
                }, status=400)
            
            # Создаем новый ответ
            print(f"Создаем новый ответ к посту {post_id}, автор: {request.user.username}")
            reply = ForumPost.objects.create(
                topic=topic,
                author=request.user,
                parent=parent_post,
                content=content
            )
            
            # Обновляем дату последнего обновления темы
            topic.updated_on = timezone.now()
            topic.save()
            
            # Рендерим HTML для нового ответа
            level = 1
            if parent_post.parent:  # Если отвечаем на вложенный ответ
                level = 2  # Для простоты ограничимся двумя уровнями вложенности
            
            print(f"Рендерим шаблон single_reply.html для ответа {reply.id}, уровень {level}")
            try:
                html = render_to_string('weightloss/forum/single_reply.html', {
                    'reply': reply,
                    'level': level,
                    'user': request.user
                }, request=request)
                print(f"Шаблон успешно отрендерен, длина HTML: {len(html)}")
            except Exception as e:
                print(f"Ошибка при рендеринге шаблона: {str(e)}")
                html = f"<div>Ответ добавлен, но не может быть отображен. Обновите страницу.</div>"
            
            return JsonResponse({
                'status': 'success',
                'html': html,
                'reply_id': reply.id,
                'parent_id': parent_post.id,
                'total_replies': parent_post.total_replies_count()
            })
        except Exception as e:
            print(f"Необработанная ошибка в ForumPostReplyView: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'message': f'Внутренняя ошибка сервера: {str(e)}'
            }, status=500)

class ForumPostDeleteView(LoginRequiredMixin, View):
    """
    Обработка AJAX-запросов на удаление ответов в форуме
    """
    def post(self, request, post_id):
        post = get_object_or_404(ForumPost, id=post_id)
        
        # Проверяем, может ли пользователь удалить этот пост
        if request.user.id != post.author.id and not request.user.is_staff:
            return JsonResponse({
                'status': 'error',
                'message': 'У вас нет прав для удаления этого ответа'
            }, status=403)
        
        # Получаем родительский пост для обновления счетчика ответов
        parent_post = post.parent
        parent_id = parent_post.id if parent_post else None
        
        # Удаляем пост и все его ответы рекурсивно
        post.delete()
        
        # Возвращаем обновленное количество ответов, если есть родительский пост
        if parent_post:
            return JsonResponse({
                'status': 'success',
                'parent_id': parent_id,
                'total_replies': parent_post.total_replies_count()
            })
        else:
            return JsonResponse({
                'status': 'success'
            })
