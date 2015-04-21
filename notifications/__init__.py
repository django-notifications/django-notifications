try:
    from notifications.signals import notify
except ImportError:
    pass

try:
    from notifications.urls import urlpatterns
    urls = (urlpatterns, 'notifications', 'notifications')
except ImportError:
    pass

__version_info__ = {
    'major': 0,
    'minor': 7,
    'micro': 0,
    'releaselevel': 'final',
    'serial': 0
}


def get_version(release_level=True):
    """
    Return the formatted version information
    """
    vers = ["%(major)i.%(minor)i.%(micro)i" % __version_info__]
    if release_level and __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s%(serial)i' % __version_info__)
    return ''.join(vers)


__version__ = get_version()
