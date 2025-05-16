from django.core.management.base import BaseCommand
from weightloss.models import Post

class Command(BaseCommand):
    help = 'Check the status of all posts in the database'

    def handle(self, *args, **options):
        # Get all posts
        posts = Post.objects.all()
        
        self.stdout.write(f"Total posts in database: {posts.count()}")
        
        # Group by status
        status_counts = {}
        for status, _ in Post.STATUS_CHOICES:
            count = Post.objects.filter(status=status).count()
            status_counts[status] = count
        
        self.stdout.write("\nPosts by status:")
        for status, count in status_counts.items():
            self.stdout.write(f"  - {status}: {count}")
        
        self.stdout.write("\nAll posts details:")
        for post in posts:
            self.stdout.write(f"ID: {post.id} | Title: {post.title} | Author: {post.author.username} | Status: {post.status} | Category: {post.category.name} | Featured image: {'Yes' if post.featured_image else 'No'}") 