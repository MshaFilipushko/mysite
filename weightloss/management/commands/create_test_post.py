from django.core.management.base import BaseCommand
from weightloss.models import Post, Category
from django.contrib.auth.models import User
from django.utils.text import slugify
import random
import string

class Command(BaseCommand):
    help = 'Create a test post for debugging'

    def handle(self, *args, **options):
        # Find first user and category
        try:
            user = User.objects.first()
            category = Category.objects.first()
            
            if not user or not category:
                self.stdout.write(self.style.ERROR("No users or categories found. Cannot create post."))
                return
                
            # Check if post with diagnostic title already exists
            title = "Диагностика проблемы отображения статей"
            existing_post = Post.objects.filter(title=title).first()
            
            if existing_post:
                self.stdout.write(f"Post already exists with ID: {existing_post.id}, Status: {existing_post.status}")
                
                # Update the status to ensure it's published
                existing_post.status = 'published'
                existing_post.save()
                self.stdout.write(self.style.SUCCESS(f"Updated post status to 'published'"))
                return
                
            # Create slug for the post
            base_slug = slugify(title)
            if not base_slug:
                random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                base_slug = f"post-{random_string}"
            
            # Create new post
            post = Post.objects.create(
                title=title,
                slug=base_slug,
                author=user,
                category=category,
                content='Тестовый контент для диагностики отображения статей в блоге.',
                status='published'
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created new test post with ID: {post.id}, Status: {post.status}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating post: {str(e)}")) 