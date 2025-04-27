from django.core.management.base import BaseCommand
from weightloss.models import Post

class Command(BaseCommand):
    help = 'Fix specific post with invalid status'

    def handle(self, *args, **options):
        # List all posts to see what we have
        self.stdout.write("All posts in the system:")
        for post in Post.objects.all():
            self.stdout.write(f"ID: {post.id}, Title: {post.title}, Status: '{post.status}'")
        
        # Find posts with invalid statuses and fix them
        fixed_count = 0
        for post in Post.objects.all():
            original_status = post.status
            
            # Fix invalid status values
            if post.status not in ['draft', 'published', 'pending', 'rejected']:
                # If it contains "published", set it to published
                if "published" in post.status.lower():
                    post.status = "published"
                    post.save()
                    self.stdout.write(f"Fixed post '{post.title}': '{original_status}' -> 'published'")
                    fixed_count += 1
                # Handle other cases
                elif len(post.status) > 10 or not post.status:
                    post.status = "draft"
                    post.save()
                    self.stdout.write(f"Fixed post '{post.title}': '{original_status}' -> 'draft'")
                    fixed_count += 1
        
        # Print results
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS(f"Fixed {fixed_count} posts with invalid statuses"))
            self.stdout.write("\nUpdated posts:")
            for post in Post.objects.all():
                self.stdout.write(f"ID: {post.id}, Title: {post.title}, Status: '{post.status}'")
        else:
            self.stdout.write(self.style.SUCCESS("No invalid post statuses found")) 