import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject10.settings')
django.setup()

from weightloss.models import Recipe
from django.utils.text import slugify
import random
import string

def fix_recipe_slugs():
    recipes = Recipe.objects.all()
    count = 0
    
    print(f"Found {len(recipes)} recipes to process")
    
    for recipe in recipes:
        old_slug = recipe.slug
        
        # Transliterate Cyrillic to Latin characters
        transliterated_title = ''
        cyrillic_to_latin = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 
            'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 
            'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        for char in recipe.title:
            transliterated_title += cyrillic_to_latin.get(char, char)
        
        base_slug = slugify(transliterated_title)
        
        if not base_slug:
            # If still no valid slug, keep the existing one
            continue
        
        unique_slug = base_slug
        counter = 1
        
        while Recipe.objects.filter(slug=unique_slug).exclude(id=recipe.id).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        
        if old_slug != unique_slug:
            recipe.slug = unique_slug
            recipe.save(update_fields=['slug'])
            count += 1
            print(f"Updated slug: {old_slug} -> {unique_slug}")
    
    print(f"Updated {count} recipe slugs")

if __name__ == "__main__":
    fix_recipe_slugs() 