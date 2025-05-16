from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix post statuses using raw SQL'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # List all posts
            cursor.execute("SELECT id, title, status FROM weightloss_post")
            posts = cursor.fetchall()
            
            self.stdout.write("Current posts in database:")
            for post in posts:
                self.stdout.write(f"ID: {post[0]}, Title: {post[1]}, Status: '{post[2]}'")
            
            # Fix post with status "213231 (published)"
            cursor.execute(
                "UPDATE weightloss_post SET status = 'published' WHERE status LIKE '%published%' AND status != 'published'"
            )
            updated_rows1 = cursor.rowcount
            
            # Fix any other invalid statuses
            cursor.execute(
                "UPDATE weightloss_post SET status = 'draft' WHERE status NOT IN ('draft', 'published', 'pending', 'rejected')"
            )
            updated_rows2 = cursor.rowcount
            
            total_updated = updated_rows1 + updated_rows2
            
            if total_updated > 0:
                self.stdout.write(self.style.SUCCESS(f"Updated {total_updated} posts with invalid statuses"))
                
                # Show updated posts
                cursor.execute("SELECT id, title, status FROM weightloss_post")
                updated_posts = cursor.fetchall()
                
                self.stdout.write("\nUpdated posts:")
                for post in updated_posts:
                    self.stdout.write(f"ID: {post[0]}, Title: {post[1]}, Status: '{post[2]}'")
            else:
                self.stdout.write(self.style.SUCCESS("No posts needed updates")) 