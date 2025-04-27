from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Recipe, Challenge, ForumCategory, ForumTopic
from django.utils import timezone

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'
    
    def items(self):
        return ['home', 'blog_list', 'recipe_list', 'calculators', 'challenge_list', 
                'forum_home', 'about', 'contact', 'privacy_policy', 'terms_of_service', 
                'cookie_policy']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()


class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7
    protocol = 'https'
    
    def items(self):
        return Post.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_on
    
    def location(self, obj):
        return obj.get_absolute_url()


class RecipeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    protocol = 'https'
    
    def items(self):
        return Recipe.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_on
    
    def location(self, obj):
        return obj.get_absolute_url()


class ChallengeSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = 'https'
    
    def items(self):
        return Challenge.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.created_on
    
    def location(self, obj):
        return obj.get_absolute_url()


class ForumCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'
    
    def items(self):
        return ForumCategory.objects.all()
    
    def lastmod(self, obj):
        # Получение последней активности в категории
        topics = obj.topics.all()
        if topics.exists():
            latest_topic = topics.order_by('-updated_on').first()
            return latest_topic.updated_on
        return timezone.now()
    
    def location(self, obj):
        return obj.get_absolute_url()


class ForumTopicSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    protocol = 'https'
    
    def items(self):
        return ForumTopic.objects.all()
    
    def lastmod(self, obj):
        return obj.updated_on
    
    def location(self, obj):
        return obj.get_absolute_url() 