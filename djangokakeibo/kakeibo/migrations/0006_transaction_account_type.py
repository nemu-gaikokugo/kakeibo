# Generated by Django 5.1.5 on 2025-02-05 13:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0005_accounttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='account_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kakeibo.accounttype'),
        ),
    ]
