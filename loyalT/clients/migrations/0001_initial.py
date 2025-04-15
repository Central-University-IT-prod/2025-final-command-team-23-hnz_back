# Generated by Django 5.1.6 on 2025-03-01 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255)),
                ('image_url', models.CharField(max_length=1024, null=True)),
            ],
        ),
    ]
