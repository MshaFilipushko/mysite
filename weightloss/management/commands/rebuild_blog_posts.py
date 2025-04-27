from django.core.management.base import BaseCommand
from weightloss.models import Post
from django.utils import timezone

class Command(BaseCommand):
    help = 'Rebuild all published blog posts by updating their timestamps'

    def handle(self, *args, **options):
        # Get all published posts
        published_posts = Post.objects.filter(status='published')
        count = published_posts.count()
        
        self.stdout.write(f"Found {count} published posts")
        
        if count > 0:
            # Update each post's updated_on timestamp
            current_time = timezone.now()
            
            for post in published_posts:
                old_time = post.updated_on
                post.updated_on = current_time
                post.save(update_fields=['updated_on'])
                self.stdout.write(f"Updated post '{post.title}' from {old_time} to {current_time}")
            
            self.stdout.write(self.style.SUCCESS(f"Successfully updated timestamps for {count} published posts"))
        else:
            self.stdout.write(self.style.WARNING("No published posts found to update")) 