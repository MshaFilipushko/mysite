from django.core.management.base import BaseCommand
from weightloss.models import Post
import json
from django.core.serializers.json import DjangoJSONEncoder

class Command(BaseCommand):
    help = 'List all post details including referenced objects'

    def handle(self, *args, **options):
        # Get all posts
        posts = Post.objects.all()
        count = posts.count()
        
        self.stdout.write(f"Found {count} total posts")
        
        # List them with detailed information
        for post in posts:
            self.stdout.write("\n" + "-" * 50)
            self.stdout.write(f"Post ID: {post.id}")
            self.stdout.write(f"Title: {post.title}")
            self.stdout.write(f"Slug: {post.slug}")
            self.stdout.write(f"Status: {post.status}")
            self.stdout.write(f"Author: {post.author.username} (ID: {post.author.id})")
            self.stdout.write(f"Category: {post.category.name} (ID: {post.category.id})")
            self.stdout.write(f"Created: {post.created_on}")
            self.stdout.write(f"Updated: {post.updated_on}")
            self.stdout.write(f"Featured: {post.is_featured}")
            self.stdout.write(f"Featured image: {'Yes' if post.featured_image else 'No'}")
            if post.featured_image:
                self.stdout.write(f"Image path: {post.featured_image.path}")
            
            # Check if content is in HTML format
            content_preview = post.content[:100] + "..." if len(post.content) > 100 else post.content
            self.stdout.write(f"Content preview: {content_preview}")
            
        self.stdout.write("\n" + "=" * 50)
        
        # Group by status
        status_counts = {}
        for status, _ in Post.STATUS_CHOICES:
            count = Post.objects.filter(status=status).count()
            status_counts[status] = count
        
        self.stdout.write("\nPosts by status:")
        for status, count in status_counts.items():
            self.stdout.write(f"  - {status}: {count}") 