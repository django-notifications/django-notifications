# -*- coding: utf-8 -*-
from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import swapper


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.CharField(default='info', max_length=20, choices=[('success', 'success'), ('info', 'info'), ('warning', 'warning'), ('error', 'error')])),
                ('unread', models.BooleanField(default=True)),
                ('actor_object_id', models.CharField(max_length=255)),
                ('verb', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('target_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('action_object_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('public', models.BooleanField(default=True)),
                ('action_object_content_type', models.ForeignKey(related_name='notify_action_object', blank=True, to='contenttypes.ContentType', null=True, on_delete=models.CASCADE)),
                ('actor_content_type', models.ForeignKey(related_name='notify_actor', to='contenttypes.ContentType', on_delete=models.CASCADE)),
                ('recipient', models.ForeignKey(related_name='notifications', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('target_content_type', models.ForeignKey(related_name='notify_target', blank=True, to='contenttypes.ContentType', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'swappable': swapper.swappable_setting('notifications', 'Notification'),
                'ordering': ('-timestamp',),
            },
            bases=(models.Model,),
        ),
    ]
