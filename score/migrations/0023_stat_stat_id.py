# Generated by Django 3.2.16 on 2023-03-10 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0022_auto_20230308_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='stat_id',
            field=models.IntegerField(null=True),
        ),
    ]
