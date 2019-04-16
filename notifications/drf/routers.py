from rest_framework import routers
from notifications.drf import views

router = routers.SimpleRouter()
router.register(r'notifications', views.NotificationViewSet, base_name='notifications')
