import os
import django

# Настраиваем окружение Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject10.settings')
django.setup()

from weightloss.models import FoodCategory, Food

# Очистка существующих данных
print("Удаление существующих данных...")
Food.objects.all().delete()
FoodCategory.objects.all().delete()

# Создание категорий продуктов
print("Создание категорий продуктов...")
categories = {
    "meat": FoodCategory.objects.create(name="Мясо и птица"),
    "fish": FoodCategory.objects.create(name="Рыба и морепродукты"),
    "dairy": FoodCategory.objects.create(name="Молочные продукты"),
    "grains": FoodCategory.objects.create(name="Крупы и злаки"),
    "vegetables": FoodCategory.objects.create(name="Овощи"),
    "fruits": FoodCategory.objects.create(name="Фрукты и ягоды"),
    "nuts": FoodCategory.objects.create(name="Орехи и семена"),
    "oils": FoodCategory.objects.create(name="Масла и жиры"),
    "sweets": FoodCategory.objects.create(name="Сладости и десерты"),
    "beverages": FoodCategory.objects.create(name="Напитки"),
}

# Добавление продуктов
print("Добавление продуктов...")
products = [
    # Мясо и птица
    {"name": "Куриная грудка", "category": categories["meat"], "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    {"name": "Говядина", "category": categories["meat"], "calories": 250, "protein": 26, "fat": 17, "carbs": 0},
    {"name": "Свинина", "category": categories["meat"], "calories": 242, "protein": 27, "fat": 14, "carbs": 0},
    {"name": "Индейка", "category": categories["meat"], "calories": 135, "protein": 29, "fat": 2, "carbs": 0},
    
    # Рыба и морепродукты
    {"name": "Лосось", "category": categories["fish"], "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    {"name": "Тунец", "category": categories["fish"], "calories": 144, "protein": 30, "fat": 1, "carbs": 0},
    {"name": "Креветки", "category": categories["fish"], "calories": 99, "protein": 24, "fat": 0.3, "carbs": 0.2},
    
    # Молочные продукты
    {"name": "Молоко 3,2%", "category": categories["dairy"], "calories": 61, "protein": 3.2, "fat": 3.2, "carbs": 4.7},
    {"name": "Творог 5%", "category": categories["dairy"], "calories": 121, "protein": 18, "fat": 5, "carbs": 3},
    {"name": "Йогурт натуральный", "category": categories["dairy"], "calories": 60, "protein": 5, "fat": 3.2, "carbs": 4},
    {"name": "Сыр твердый", "category": categories["dairy"], "calories": 350, "protein": 25, "fat": 27, "carbs": 0},
    
    # Крупы и злаки
    {"name": "Гречка", "category": categories["grains"], "calories": 343, "protein": 12.6, "fat": 3.3, "carbs": 68},
    {"name": "Рис", "category": categories["grains"], "calories": 330, "protein": 7, "fat": 0.6, "carbs": 78},
    {"name": "Овсянка", "category": categories["grains"], "calories": 366, "protein": 12, "fat": 6.2, "carbs": 68},
    {"name": "Киноа", "category": categories["grains"], "calories": 368, "protein": 14, "fat": 6, "carbs": 64},
    
    # Овощи
    {"name": "Брокколи", "category": categories["vegetables"], "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
    {"name": "Морковь", "category": categories["vegetables"], "calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
    {"name": "Шпинат", "category": categories["vegetables"], "calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6},
    {"name": "Помидоры", "category": categories["vegetables"], "calories": 20, "protein": 0.9, "fat": 0.2, "carbs": 4.2},
    {"name": "Огурцы", "category": categories["vegetables"], "calories": 16, "protein": 0.8, "fat": 0.1, "carbs": 3.6},
    
    # Фрукты и ягоды
    {"name": "Яблоки", "category": categories["fruits"], "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
    {"name": "Бананы", "category": categories["fruits"], "calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
    {"name": "Апельсины", "category": categories["fruits"], "calories": 43, "protein": 0.9, "fat": 0.1, "carbs": 11},
    {"name": "Черника", "category": categories["fruits"], "calories": 57, "protein": 0.7, "fat": 0.3, "carbs": 14},
    
    # Орехи и семена
    {"name": "Миндаль", "category": categories["nuts"], "calories": 576, "protein": 21, "fat": 49, "carbs": 22},
    {"name": "Грецкие орехи", "category": categories["nuts"], "calories": 654, "protein": 15, "fat": 65, "carbs": 14},
    {"name": "Семена чиа", "category": categories["nuts"], "calories": 486, "protein": 17, "fat": 31, "carbs": 42},
    
    # Масла и жиры
    {"name": "Оливковое масло", "category": categories["oils"], "calories": 884, "protein": 0, "fat": 100, "carbs": 0},
    {"name": "Сливочное масло", "category": categories["oils"], "calories": 748, "protein": 0.6, "fat": 82, "carbs": 0.6},
    
    # Сладости и десерты
    {"name": "Темный шоколад", "category": categories["sweets"], "calories": 546, "protein": 7.8, "fat": 31, "carbs": 61},
    {"name": "Мед", "category": categories["sweets"], "calories": 304, "protein": 0.3, "fat": 0, "carbs": 82},
    
    # Напитки
    {"name": "Кофе (черный)", "category": categories["beverages"], "calories": 2, "protein": 0.1, "fat": 0, "carbs": 0},
    {"name": "Зеленый чай", "category": categories["beverages"], "calories": 1, "protein": 0, "fat": 0, "carbs": 0.3},
]

for product in products:
    Food.objects.create(
        name=product["name"],
        category=product["category"],
        calories=product["calories"],
        protein=product["protein"],
        fats=product["fat"],
        carbs=product["carbs"]
    )

print(f"Добавлено {len(products)} продуктов в {len(categories)} категорий.")
print("Готово!") 