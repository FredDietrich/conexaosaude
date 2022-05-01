from django import template
register = template.Library()

@register.inclusion_tag('nav.html', takes_context=True)
def navbar(context):
    return {
        'form': context['form']
    }

@register.inclusion_tag('pagination.html', takes_context=True)
def pagination(context):
    return {
        'page_obj': context['page_obj']
    }