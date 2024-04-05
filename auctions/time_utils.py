import pytz
import requests
import geoip2.database
from django.utils import timezone


def get_timezone_by_ip(ip_address):
    if ip_address == '127.0.0.1':
        return pytz.timezone('Europe/Berlin')

    url = 'https://f005.backblazeb2.com/file/commerce-database/GeoLite2-City.mmdb'
    response = requests.get(url)

    if response.status_code == 200:
        # Use the database file with geoip2 library
        reader = geoip2.database.Reader(response.content)
        try:
            response = reader.city(ip_address)
            timezone_str = response.location.time_zone
            return pytz.timezone(timezone_str)
        except geoip2.errors.AddressNotFoundError:
            return pytz.timezone('UTC')
        finally:
            reader.close()

    else:
        # Handle errors, fallback to a default timezone, etc.
        return pytz.timezone('UTC')




def set_timezone(view_func):
    def wrapper(request, *args, **kwargs):
        client_ip = request.META.get('REMOTE_ADDR')
        current_timezone = get_timezone_by_ip(client_ip)    
        timezone.activate(current_timezone)  # Set desired timezone
        return view_func(request, *args, **kwargs)
    return wrapper
