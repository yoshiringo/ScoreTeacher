# Generated by Django 3.2.16 on 2023-03-11 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0026_remove_stat_stat_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='stat_number',
            field=models.IntegerField(null=True),
        ),
    ]
