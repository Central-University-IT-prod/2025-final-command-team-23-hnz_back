# Generated by Django 5.1.6 on 2025-03-02 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_item_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'active'), ('INACTIVE', 'inactive')], default='ACTIVE', max_length=8),
        ),
    ]
