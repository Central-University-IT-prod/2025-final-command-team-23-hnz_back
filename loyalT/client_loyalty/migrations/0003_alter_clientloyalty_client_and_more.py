# Generated by Django 5.1.6 on 2025-03-02 08:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_loyalty', '0002_initial'),
        ('clients', '0001_initial'),
        ('companies', '0004_company_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientloyalty',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_loyalty', to='clients.client'),
        ),
        migrations.AlterField(
            model_name='clientloyalty',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_loyalty', to='companies.company'),
        ),
    ]
