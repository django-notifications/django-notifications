import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0007_add_timestamp_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4),
        ),
    ]
