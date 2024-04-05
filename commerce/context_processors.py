from django.utils import timezone

def timezone_context(request):
    return {'current_timezone': timezone.get_current_timezone()}
