# Generated by Django 3.2.16 on 2022-10-22 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detail',
            name='patt',
        ),
        migrations.RemoveField(
            model_name='person',
            name='color',
        ),
        migrations.AddField(
            model_name='detail',
            name='putt',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='パーオン'),
        ),
        migrations.AlterField(
            model_name='detail',
            name='fw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='FWキープ'),
        ),
        migrations.AlterField(
            model_name='detail',
            name='ob',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='OB'),
        ),
        migrations.AlterField(
            model_name='detail',
            name='par_on',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='パーオン'),
        ),
        migrations.AlterField(
            model_name='detail',
            name='penalty',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='ペナルティ'),
        ),
        migrations.AlterField(
            model_name='detail',
            name='total_score',
            field=models.PositiveSmallIntegerField(verbose_name='スコア'),
        ),
    ]