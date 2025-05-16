from django.core.management.base import BaseCommand
from weightloss.models import Post, Recipe, ForumTopic, VIPPost
from weightloss.utils import generate_unique_slug

class Command(BaseCommand):
    help = 'Обновляет slug-и существующих статей, рецептов, тем форума и VIP-статей, которые начинаются с дефиса'

    def handle(self, *args, **options):
        # Обновление статей блога
        posts = Post.objects.filter(slug__startswith='-')
        self.stdout.write(f'Найдено {posts.count()} статей с некорректными slug-ами')
        
        for post in posts:
            old_slug = post.slug
            post.slug = generate_unique_slug(Post, post.title, post)
            post.save(update_fields=['slug'])
            self.stdout.write(f'Обновлен slug для статьи "{post.title}": {old_slug} -> {post.slug}')
        
        # Обновление рецептов
        recipes = Recipe.objects.filter(slug__startswith='-')
        self.stdout.write(f'Найдено {recipes.count()} рецептов с некорректными slug-ами')
        
        for recipe in recipes:
            old_slug = recipe.slug
            recipe.slug = generate_unique_slug(Recipe, recipe.title, recipe)
            recipe.save(update_fields=['slug'])
            self.stdout.write(f'Обновлен slug для рецепта "{recipe.title}": {old_slug} -> {recipe.slug}')
        
        # Обновление тем форума
        topics = ForumTopic.objects.filter(slug__startswith='-')
        self.stdout.write(f'Найдено {topics.count()} тем форума с некорректными slug-ами')
        
        for topic in topics:
            old_slug = topic.slug
            topic.slug = generate_unique_slug(ForumTopic, topic.title, topic)
            topic.save(update_fields=['slug'])
            self.stdout.write(f'Обновлен slug для темы форума "{topic.title}": {old_slug} -> {topic.slug}')
        
        # Обновление VIP-статей
        vip_posts = VIPPost.objects.filter(slug__startswith='-')
        self.stdout.write(f'Найдено {vip_posts.count()} VIP-статей с некорректными slug-ами')
        
        for vip_post in vip_posts:
            old_slug = vip_post.slug
            vip_post.slug = generate_unique_slug(VIPPost, vip_post.title, vip_post)
            vip_post.save(update_fields=['slug'])
            self.stdout.write(f'Обновлен slug для VIP-статьи "{vip_post.title}": {old_slug} -> {vip_post.slug}')
            
        self.stdout.write(self.style.SUCCESS('Все slug-и успешно обновлены!')) 