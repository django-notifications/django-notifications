import importlib

from notifications import settings as notifications_settings

_GenericNotificationRelatedField = notifications_settings.get_config()['FIELDS']['generic_relation']
_UserSerializer = notifications_settings.get_config()['SERIALIZERS']['user']


def _import(klass):
    # split it
    splitted = klass.split('.')
    class_name = splitted.pop(-1)  # last element
    module_name = '.'.join(splitted)

    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


def get_related_field():
    return _import(_GenericNotificationRelatedField)


def get_user_serializer():
    return _import(_UserSerializer)
