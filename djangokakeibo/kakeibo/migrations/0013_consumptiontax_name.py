# Generated by Django 5.1.5 on 2025-02-17 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0012_rename_counter_party_transaction_counterparty_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumptiontax',
            name='name',
            field=models.CharField(default=1, max_length=255, verbose_name='税の種類'),
            preserve_default=False,
        ),
    ]
