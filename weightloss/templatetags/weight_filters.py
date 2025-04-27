from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Вычитает arg из value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Делит value на arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Умножает value на arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def bmi_category(bmi):
    """Возвращает категорию ИМТ на основе значения"""
    try:
        bmi = float(bmi)
        if bmi < 18.5:
            return "Недостаточный"
        elif bmi < 25:
            return "Нормальный"
        elif bmi < 30:
            return "Избыточный"
        else:
            return "Ожирение"
    except (ValueError, TypeError):
        return "Неизвестно"

@register.filter
def min(value, arg):
    """Возвращает минимальное из двух значений"""
    try:
        value_float = float(value)
        arg_float = float(arg)
        return value_float if value_float < arg_float else arg_float
    except (ValueError, TypeError):
        return value

@register.filter
def max(value, arg):
    """Возвращает максимальное из двух значений"""
    try:
        value_float = float(value)
        arg_float = float(arg)
        return value_float if value_float > arg_float else arg_float
    except (ValueError, TypeError):
        return value

@register.filter
def sum(iterable, attr):
    """Суммирует значения атрибута attr для всех объектов в iterable"""
    total = 0
    for item in iterable:
        try:
            value = getattr(item, attr)
            if callable(value):
                value = value()
            total += value
        except (ValueError, TypeError, AttributeError):
            pass
    return total

@register.filter
def add_class(field, css_class):
    """Добавляет css класс к полю формы"""
    return field.as_widget(attrs={"class": css_class})

@register.filter
def is_admin(user):
    """Проверяет, является ли пользователь администратором (staff или superuser)"""
    return user.is_staff or user.is_superuser 