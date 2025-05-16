from django.urls import resolve
from djangoProject10.seo import DEFAULT_SEO, SECTION_SEO
import json

def seo_processor(request):
    """
    Контекстный процессор для добавления SEO-метаданных в контекст шаблонов.
    """
    context = {
        'seo': DEFAULT_SEO.copy()
    }
    
    # Определяем раздел сайта на основе URL
    url_name = resolve(request.path_info).url_name
    
    # Маппинг URL на разделы сайта
    section_mapping = {
        'home': 'home',
        'blog_list': 'blog',
        'blog_detail': 'blog',
        'recipe_list': 'recipes',
        'recipe_detail': 'recipes',
        'forum_home': 'forum',
        'forum_category': 'forum',
        'forum_topic_detail': 'forum',
        'challenge_list': 'challenges',
        'challenge_detail': 'challenges',
    }
    
    # Если текущий URL соответствует определенному разделу, обновляем SEO-данные
    section = section_mapping.get(url_name)
    if section and section in SECTION_SEO:
        context['seo'].update(SECTION_SEO[section])
    
    # Добавляем каноническую ссылку с учетом текущего URL
    if 'canonical_url' in context['seo']:
        base_url = context['seo']['canonical_url'].rstrip('/')
        context['seo']['canonical_url'] = f"{base_url}{request.path}"
    
    # Кодируем структурированные данные Schema.org в JSON-LD
    from djangoProject10.seo import SCHEMA_ORG
    context['schema_org'] = {
        'website': json.dumps(SCHEMA_ORG['website']),
        'organization': json.dumps(SCHEMA_ORG['organization']),
    }
    
    return context 