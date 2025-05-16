import random
import string
from django.utils.text import slugify
from unidecode import unidecode

def generate_unique_slug(model_class, title, instance=None):
    """
    Генерирует уникальный slug для модели из заголовка.
    
    Аргументы:
        model_class: Класс модели, для которой создается slug
        title: Заголовок, из которого формируется slug
        instance: Экземпляр объекта (при редактировании)
    
    Возвращает:
        Уникальный slug
    """
    # Очищаем заголовок от лишних пробелов
    title = title.strip()
    
    # Транслитерация кириллицы в латиницу
    transliterated = unidecode(title)
    
    # Создаем базовый slug
    base_slug = slugify(transliterated)
    
    # Если slug пустой (может быть для очень коротких или странных заголовков)
    if not base_slug:
        # Ручная транслитерация для русских букв
        ru_en_chars = {
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
        
        manual_transliterated = ""
        for char in title:
            manual_transliterated += ru_en_chars.get(char, char)
            
        # Создаем slug из ручной транслитерации
        base_slug = slugify(manual_transliterated)
        
        # Если все еще пустой slug, используем первые буквы + случайный суффикс
        if not base_slug:
            # Генерируем случайную строку
            random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            base_slug = f"post-{random_string}"
    
    # Проверяем уникальность slug
    unique_slug = base_slug
    counter = 1
    
    # Исключаем текущий экземпляр из проверки уникальности (при редактировании)
    query = model_class.objects.filter(slug=unique_slug)
    if instance and instance.pk:
        query = query.exclude(pk=instance.pk)
    
    # Если slug уже существует, добавляем к нему числовой суффикс
    while query.exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
        query = model_class.objects.filter(slug=unique_slug)
        if instance and instance.pk:
            query = query.exclude(pk=instance.pk)
    
    return unique_slug 