from django.core.management.base import BaseCommand
from weightloss.models import Post
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test post views to ensure they correctly load posts by status'

    def handle(self, *args, **options):
        try:
            # Get first user
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR("No users found. Cannot test view."))
                return
            
            # Get posts directly using the queries from the view
            all_posts = Post.objects.filter(author=user).order_by('-created_on')
            published_posts = all_posts.filter(status='published')
            pending_posts = all_posts.filter(status='pending')
            draft_posts = all_posts.filter(status='draft')
            rejected_posts = all_posts.filter(status='rejected')
            
            # Print results
            self.stdout.write(f"All posts: {all_posts.count()}")
            self.stdout.write(f"Published posts: {published_posts.count()}")
            self.stdout.write(f"Pending posts: {pending_posts.count()}")
            self.stdout.write(f"Draft posts: {draft_posts.count()}")
            self.stdout.write(f"Rejected posts: {rejected_posts.count()}")
            
            # Print details of published posts
            self.stdout.write("\nPublished posts details:")
            for post in published_posts:
                self.stdout.write(f"ID: {post.id}, Title: {post.title}, Status: {post.status}")
            
            # Print details of all posts
            self.stdout.write("\nAll posts details:")
            for post in all_posts:
                self.stdout.write(f"ID: {post.id}, Title: {post.title}, Status: {post.status}")
            
            self.stdout.write(self.style.SUCCESS("Test completed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing view: {str(e)}")) 