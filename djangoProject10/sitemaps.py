from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from weightloss.models import Post, Recipe, Category, Challenge, ForumCategory, ForumTopic

class StaticViewSitemap(Sitemap):
    """Карта сайта для статических страниц"""
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return ['home', 'blog_list', 'recipe_list', 'forum_home', 'challenge_list', 'about', 'contact']

    def location(self, item):
        return reverse(item)

class BlogPostSitemap(Sitemap):
    """Карта сайта для статей блога"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_on or obj.created_on

class RecipeSitemap(Sitemap):
    """Карта сайта для рецептов"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Recipe.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_on or obj.created_on

class CategorySitemap(Sitemap):
    """Карта сайта для категорий блога"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Category.objects.all()

class ChallengeSitemap(Sitemap):
    """Карта сайта для челленджей"""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Challenge.objects.filter(is_active=True)

class ForumCategorySitemap(Sitemap):
    """Карта сайта для категорий форума"""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return ForumCategory.objects.all()

class ForumTopicSitemap(Sitemap):
    """Карта сайта для тем форума"""
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        # Ограничиваем количество тем форума, чтобы не перегружать карту сайта
        return ForumTopic.objects.all().order_by('-created_on')[:100]

    def lastmod(self, obj):
        return obj.updated_on or obj.created_on 