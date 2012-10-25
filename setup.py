from distutils.core import setup
from notifications import __version__

setup(name='django-notifications-hq',
      version=__version__,
      description='GitHub notifications alike app for Django.',
      long_description=open('README.rst').read(),
      author='Brant Young',
      author_email='brant.young@gmail.com',
      url='http://github.com/brantyoung/django-notifications',
      install_requires=[
          'django>=1.4',
          'django-model-utils>=1.1.0'
      ],
      packages=['notifications',
                'notifications.templatetags',
                'notifications.migrations'
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
