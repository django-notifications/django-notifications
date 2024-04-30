from typing import Any, Dict, List, Union

from django.core.exceptions import ImproperlyConfigured
from django.forms import model_to_dict

from notifications.settings import notification_settings


def get_limit(request):
    default_num_to_fetch = notification_settings.NUM_TO_FETCH
    try:
        # If they don't specify, make it 5.
        num_to_fetch = request.GET.get("limit", default_num_to_fetch)
        num_to_fetch = int(num_to_fetch)
        if not 1 <= num_to_fetch <= 100:
            num_to_fetch = default_num_to_fetch
    except ValueError:  # If casting to an int fails.
        num_to_fetch = default_num_to_fetch
    return num_to_fetch


def queryset_to_dict(notifications, limit: int) -> List[Dict[str, Any]]:
    notification_list = []
    for notification in notifications[0:limit]:
        struct = model_to_dict(notification)
        struct["slug"] = notification.id
        if notification.actor:
            struct["actor"] = str(notification.actor)
        if notification.target:
            struct["target"] = str(notification.target)
        if notification.action_object:
            struct["action_object"] = str(notification.action_object)
        if notification.data:
            struct["data"] = notification.data
        notification_list.append(struct)
    return notification_list


def assert_soft_delete() -> None:
    if not notification_settings.SOFT_DELETE:
        msg = "To use this feature you need activate SOFT_DELETE in settings.py"
        raise ImproperlyConfigured(msg)


def str_to_bool(value: Union[str, bool]) -> bool:
    return str(value).lower() in ("t", "true", "y", "yes", "1")
