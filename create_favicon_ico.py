"""
Скрипт для создания favicon.ico
"""
from PIL import Image
import os

# Проверяем, существует ли уже файл favicon.png
if os.path.exists('static/images/favicon.png'):
    # Открываем существующий PNG favicon
    favicon_png = Image.open('static/images/favicon.png')
    
    # Сохраняем в формате ICO в корне статической директории
    favicon_png.save('static/favicon.ico', format='ICO')
    
    print("Favicon.ico создан успешно в директории static/")
else:
    print("Ошибка: Файл static/images/favicon.png не найден") 