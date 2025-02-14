# Generated by Django 4.2.19 on 2025-02-14 19:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0008_index_together_recipient_unread'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ('-timestamp',), 'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications'},
        ),
        migrations.RenameIndex(
            model_name='notification',
            new_name='notificatio_recipie_8bedf2_idx',
            old_fields=('recipient', 'unread'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='action_object_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notify_action_object', to='contenttypes.contenttype', verbose_name='action object content type'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='action_object_object_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='action object object id'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='actor_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notify_actor', to='contenttypes.contenttype', verbose_name='actor content type'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='actor_object_id',
            field=models.CharField(max_length=255, verbose_name='actor object id'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='data',
            field=jsonfield.fields.JSONField(blank=True, null=True, verbose_name='data'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='deleted',
            field=models.BooleanField(db_index=True, default=False, verbose_name='deleted'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='emailed',
            field=models.BooleanField(db_index=True, default=False, verbose_name='emailed'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='level',
            field=models.CharField(choices=[('success', 'success'), ('info', 'info'), ('warning', 'warning'), ('error', 'error')], default='info', max_length=20, verbose_name='level'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='public',
            field=models.BooleanField(db_index=True, default=True, verbose_name='public'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='recipient'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='target_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notify_target', to='contenttypes.contenttype', verbose_name='target content type'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='target_object_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='target object id'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='timestamp'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='unread',
            field=models.BooleanField(db_index=True, default=True, verbose_name='unread'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='verb',
            field=models.CharField(max_length=255, verbose_name='verb'),
        ),
    ]
