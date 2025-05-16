"""
Скрипт для создания favicon.png и apple-touch-icon.png с иконкой листика
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Создаем директорию для изображений, если она не существует
os.makedirs('static/images', exist_ok=True)

# Размеры иконок
favicon_size = (32, 32)
apple_icon_size = (180, 180)

def create_leaf_icon(size):
    """Создает иконку с листиком заданного размера"""
    # Создаем изображение с прозрачным фоном
    icon = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Зеленый цвет для листика (#4caf50)
    green_color = (76, 175, 80, 255)
    
    # Расчет размера листика
    width, height = size
    padding = int(width * 0.15)  # 15% отступ от краев
    leaf_width = width - 2 * padding
    leaf_height = height - 2 * padding
    
    # Рисуем простую форму листика (овал с заостренным концом)
    x1, y1 = padding, padding
    x2, y2 = width - padding, height - padding
    
    # Рисуем базовый овал
    draw.ellipse((x1, y1, x2, y2), fill=green_color)
    
    # Добавляем "хвостик" листика
    stem_width = int(width * 0.1)
    stem_x = width // 2
    stem_y = height - padding // 2
    draw.rectangle((stem_x - stem_width//2, height - padding, 
                    stem_x + stem_width//2, stem_y), 
                   fill=green_color)
    
    # Добавляем прожилку листика
    vein_width = int(width * 0.05)
    draw.line((width//2, y1 + padding//2, width//2, y2 - padding//2), 
              fill=(255, 255, 255, 180), width=vein_width)
    
    return icon

# Создаем favicon.png (32x32)
favicon = create_leaf_icon(favicon_size)
favicon.save('static/images/favicon.png')

# Создаем apple-touch-icon.png (180x180)
apple_icon = create_leaf_icon(apple_icon_size)
apple_icon.save('static/images/apple-touch-icon.png')

print("Favicon и Apple Touch Icon созданы успешно в директории static/images/") 