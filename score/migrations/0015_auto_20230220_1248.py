# Generated by Django 3.2.16 on 2023-02-20 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0014_rename_login_user_id_person_login_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='age',
            field=models.IntegerField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='sex',
            field=models.CharField(default=1, max_length=4),
            preserve_default=False,
        ),
    ]