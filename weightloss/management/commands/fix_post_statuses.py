from django.core.management.base import BaseCommand
from weightloss.models import Post

class Command(BaseCommand):
    help = 'Fix invalid post statuses'

    def handle(self, *args, **options):
        # Get all posts
        posts = Post.objects.all()
        
        # Output details of all posts
        self.stdout.write("Current posts in the system:")
        for post in posts:
            self.stdout.write(f"ID: {post.id}, Title: {post.title}, Status: '{post.status}'")
        
        # Count posts with invalid statuses
        valid_statuses = dict(Post.STATUS_CHOICES).keys()
        invalid_posts = [post for post in posts if post.status not in valid_statuses]
        
        if invalid_posts:
            self.stdout.write(self.style.WARNING(f"Found {len(invalid_posts)} posts with invalid statuses"))
            
            # Fix invalid statuses
            for post in invalid_posts:
                old_status = post.status
                # If it contains "published", set to published
                if "published" in old_status.lower():
                    post.status = "published"
                # Otherwise set to draft
                else:
                    post.status = "draft"
                    
                post.save()
                self.stdout.write(f"Fixed post '{post.title}': '{old_status}' -> '{post.status}'")
                
            self.stdout.write(self.style.SUCCESS("Fixed all invalid post statuses"))
        else:
            self.stdout.write(self.style.SUCCESS("No invalid post statuses found")) 