from django import template
from posters.models import Conference

register = template.Library()

@register.simple_tag(name='get_conferences')
def all_conferences():
    return Conference.objects.order_by('-date_to')
