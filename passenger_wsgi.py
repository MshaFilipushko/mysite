# -*- coding: utf-8 -*-
import os,sys

# Путь к проекту Django
sys.path.insert(0, '/var/www/u3118324/data/www/zdovoviyves.ru')
sys.path.insert(1, '/var/www/u3118324/data/djangoenv/lib/python3.10/site-packages')

# Указываем Django, где находятся настройки проекта
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoProject10.settings'
# Комментируем или меняем на True для тестирования
os.environ['DJANGO_DEBUG'] = 'False'
#os.environ['DJANGO_DEBUG'] = 'True'  # Временно включаем DEBUG

# Импортируем приложение WSGI из Django
from django.core.wsgi import get_wsgi_application

# Создаем переменную application для Passenger
application = get_wsgi_application()