# Generated by Django 5.1.6 on 2025-03-02 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
