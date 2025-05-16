#!/usr/bin/env python
import os
import sys
import django
import random
import string

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject10.settings')
django.setup()

from django.utils.text import slugify
from weightloss.models import VIPPost

def fix_empty_slugs():
    """Находит и исправляет VIP-посты с пустыми слагами"""
    try:
        # Сначала распечатаем все VIP-посты для анализа
        all_posts = VIPPost.objects.all()
        print(f"Всего VIP-постов в базе: {len(all_posts)}")
        for post in all_posts:
            print(f"ID: {post.id}, Title: {post.title}, Slug: '{post.slug}'")
        
        # Теперь проверим посты с пустыми слагами
        empty_slug_posts = VIPPost.objects.filter(slug='')
        print(f'\nНайдено {len(empty_slug_posts)} постов с пустыми слагами:')
        
        for post in empty_slug_posts:
            print(f"ID: {post.id}, Title: {post.title}")
            
            # Создаем базовый слаг из заголовка
            base_slug = slugify(post.title)
            print(f"Базовый слаг из заголовка: '{base_slug}'")
            
            # Если не получилось создать слаг из заголовка, используем случайную строку
            if not base_slug:
                random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                base_slug = f"vip-post-{random_string}"
                print(f"Сгенерирован случайный слаг: '{base_slug}'")
            
            # Проверка уникальности слага
            unique_slug = base_slug
            counter = 1
            
            while VIPPost.objects.filter(slug=unique_slug).exclude(id=post.id).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
                print(f"Проверка уникальности: '{unique_slug}'")
            
            # Присваиваем уникальный слаг и сохраняем
            print(f"Старый слаг: '{post.slug}'")
            post.slug = unique_slug
            post.save()
            print(f"Исправлено! Новый слаг: '{post.slug}'")
        
        print("\nОбработка завершена!")
        
        # Проверим, остались ли посты с пустыми слагами
        remaining_empty = VIPPost.objects.filter(slug='').count()
        if remaining_empty > 0:
            print(f"ВНИМАНИЕ: После обработки все еще осталось {remaining_empty} постов с пустыми слагами")
        else:
            print("Проверка: все посты теперь имеют непустые слаги.")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_empty_slugs() 