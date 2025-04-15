# Generated by Django 5.1.6 on 2025-03-01 22:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientLoyalty',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('points', models.BigIntegerField(default=0)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.client')),
            ],
        ),
    ]
