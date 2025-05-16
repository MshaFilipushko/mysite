from django import template
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def user_display_name(user):
    """
    Отображает имя пользователя с VIP-бэйджем, если у пользователя есть активный VIP-статус.
    Также отображает бэйдж администратора, если пользователь является администратором.
    Администратор имеет приоритет над VIP-статусом (админу не показывается VIP-бэйдж).
    """
    if user is None:
        return ""
        
    if not isinstance(user, User):
        return str(user)
        
    result = user.username
    
    # Проверка на администратора (приоритет над VIP)
    if user.is_superuser:
        # Для администраторов возвращаем только имя пользователя без бейджей,
        # так как бейдж админа отображается на страницах через другие средства
        return result
    
    # Проверка на VIP-статус (только для не-администраторов)
    if hasattr(user, 'profile') and user.profile.has_active_vip():
        vip_badge = '<span class="badge bg-warning text-dark ms-1" title="VIP-пользователь">VIP</span>'
        result = f"{result} {vip_badge}"
    
    return mark_safe(result) 