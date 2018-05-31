''' Django notifications signal file '''
from django.dispatch import Signal

notify = Signal(providing_args=[  # pylint: disable=invalid-name
    'recipient', 'actor', 'verb', 'action_object', 'target', 'description',
    'timestamp', 'level'
])
