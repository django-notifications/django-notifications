from distutils.core import setup
from notifications import __version__

setup(name='django-notifications-hq',
      version=__version__,
      description='GitHub notifications alike app for Django.',
      long_description=open('README.rst').read(),
      author='django-notifications team',
      author_email='yang@yangyubo.com',
      url='http://github.com/django-notifications/django-notifications',
      install_requires=[
          'django>=1.4',
          'django-model-utils>=2.0.3',
          'six>=1.9.0',
          'jsonfield>=1.0.3',
      ],
      test_requires=[
          'django>=1.4',
          'django-model-utils>=2.0.3',
          'six>=1.9.0',
          'jsonfield>=1.0.3',
          'pytz'
      ],
      packages=['notifications',
                'notifications.templatetags',
                'notifications.migrations',
                'notifications.south_migrations'
               ],
      package_data={'notifications': [
                                 'templates/notifications/*.html']},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
