#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Django notification setup file for pip package '''
import ast
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # pylint: disable=no-name-in-module,import-error


_version_re = re.compile(r'__version__\s+=\s+(.*)')  # pylint: disable=invalid-name

with open('notifications/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(  # pylint: disable=invalid-name
        f.read().decode('utf-8')).group(1)))


setup(
    name='django-notifications-hq',
    version=version,
    description='GitHub notifications alike app for Django.',
    long_description=open('README.rst').read(),
    author='django-notifications team',
    author_email='yang@yangyubo.com',
    url='http://github.com/django-notifications/django-notifications',
    install_requires=[
        'django>=1.7',
        'django-model-utils>=2.0.3',
        'jsonfield>=1.0.3',
        'pytz',
        'swapper'
    ],
    test_requires=[
        'django>=1.7',
        'django-model-utils>=2.0.3',
        'jsonfield>=1.0.3',
        'pytz'
    ],
    packages=[
        'notifications',
        'notifications.base',
        'notifications.templatetags',
        'notifications.migrations',
    ],
    package_data={
        'notifications': ['templates/notifications/*.html', 'static/notifications/*.js']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.7',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities'
    ],
    keywords='django notifications github action event stream',
    license='MIT',
)
