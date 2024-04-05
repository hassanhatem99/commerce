from django import template
from django.utils.timesince import timesince
from datetime import datetime, timedelta
from django.utils.timezone import localtime
from django.utils import timezone

register = template.Library()

@register.filter
def custom_timesince(value):
    now = timezone.now()
    if not timezone.is_aware(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    diff = now - value

    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() // 60)
        if mins == 1:
            return '1 min ago'
        else:
            return f'{mins} mins ago'
        
    elif diff < timedelta(days=1):
        hrs = int(diff.total_seconds() // 3600)
        if hrs == 1: 
            return '1 hour ago'
        else:
            return f'{hrs} hours ago'
        
    elif diff < timedelta(days=30):
        days = int(diff.total_seconds() // 86400)
        if days == 1:
            return '1 day ago'
        else:
            return f'{days} days ago'
        
    elif diff < timedelta(days=365):
        months = int(diff.total_seconds() // 2592000)
        if months == 1:
            return '1 month ago'
        else:
            return f'{months} months ago'
    else:
        years = int(diff.total_seconds() // 31536000)
        if years == 1:
            return '1 year ago'
        else:
            return f'{years} years ago'
        
    


@register.filter
def custom_localtime(value):
    return localtime(value)


@register.filter
def lowercase(value):
    return value.lower()

