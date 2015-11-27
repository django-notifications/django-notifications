try:
    from notifications.signals import notify
except ImportError:
    pass

try:
    from notifications.urls import urlpatterns
    urls = (urlpatterns, 'notifications', 'notifications')
except ImportError:
    pass
