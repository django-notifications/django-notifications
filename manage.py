#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # if 'test' in sys.argv or 'NOTIFICATION_TEST' in os.environ.keys():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notifications.tests.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
