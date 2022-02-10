from django.forms import model_to_dict
from notifications.utils import id2slug
from notifications.settings import get_config

def get_object_url(instance, notification, request):
    """
    Get url representing the instance object.
    This will return instance.get_url_for_notifications()
    with parameters `notification` and `request`,
    if it is defined and get_absolute_url() otherwise
    """
    if hasattr(instance, 'get_url_for_notifications'):
        return instance.get_url_for_notifications(notification, request)
    elif hasattr(instance, 'get_absolute_url'):
        return instance.get_absolute_url()
    return None

def get_num_to_fetch(request):
    default_num_to_fetch = get_config()['NUM_TO_FETCH']
    try:
        # If they don't specify, make it 5.
        num_to_fetch = request.GET.get('max', default_num_to_fetch)
        num_to_fetch = int(num_to_fetch)
        if not (1 <= num_to_fetch <= 100):
            num_to_fetch = default_num_to_fetch
    except ValueError:  # If casting to an int fails.
        num_to_fetch = default_num_to_fetch
    return num_to_fetch

def get_notification_list(request, method_name='all'):
    num_to_fetch = get_num_to_fetch(request)
    notification_list = []
    for notification in getattr(request.user.notifications, method_name)()[0:num_to_fetch]:
        struct = model_to_dict(notification)
        struct['slug'] = id2slug(notification.id)
        if notification.actor:
            struct['actor'] = str(notification.actor)
            actor_url = get_object_url(
                notification.actor, notification, request)
            if actor_url:
                struct['actor_url'] = actor_url
        if notification.target:
            struct['target'] = str(notification.target)
            target_url = get_object_url(
                notification.target, notification, request)
            if target_url:
                struct['target_url'] = target_url
        if notification.action_object:
            struct['action_object'] = str(notification.action_object)
            action_object_url = get_object_url(
                notification.action_object, notification, request)
            if action_object_url:
                struct['action_object_url'] = action_object_url
        if notification.data:
            struct['data'] = notification.data
        notification_list.append(struct)
        if request.GET.get('mark_as_read'):
            notification.mark_as_read()
    return notification_list
