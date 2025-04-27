from django.core.management.base import BaseCommand
from weightloss.models import Post

class Command(BaseCommand):
    help = 'Set all posts to published status'

    def handle(self, *args, **options):
        # Get all posts that are not published
        unpublished_posts = Post.objects.exclude(status='published')
        count = unpublished_posts.count()
        
        if count > 0:
            # Update all to published
            unpublished_posts.update(status='published')
            self.stdout.write(self.style.SUCCESS(f'Successfully published {count} posts'))
        else:
            self.stdout.write(self.style.SUCCESS('No unpublished posts found'))
            
        # Display summary of all posts
        total = Post.objects.count()
        published = Post.objects.filter(status='published').count()
        self.stdout.write(f'Total posts: {total}')
        self.stdout.write(f'Published posts: {published}') 