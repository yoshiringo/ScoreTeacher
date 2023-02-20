from email.policy import default
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

COLOR_CHOICES = (('primary', 'primary'),
                 ('secondary', 'secondary'),
                 ('success', 'success'),
                 ('info', 'info'),
                 ('warning', 'warning'),
                 ('danger', 'danger'),
                 ('light', 'light'),
                 ('dark', 'dark'))

class Person(models.Model):
    name = models.CharField(max_length=32)
    login_user = models.IntegerField(null=True)
    
    def __str__(self):
        return f'#{self.pk} {self.name}'
    
class Stat(models.Model):
    player = models.ForeignKey(to=Person, verbose_name='プレイヤー', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='日付')
    total_score = models.PositiveSmallIntegerField(verbose_name='スコア', blank=False, null=False)
    ob = models.PositiveSmallIntegerField(verbose_name='OB', blank=True, null=True)
    penalty = models.PositiveSmallIntegerField(verbose_name='ペナルティ', blank=True, null=True)
    fw = models.PositiveSmallIntegerField(verbose_name='FWキープ率', blank=True, null=True)
    par_on = models.PositiveSmallIntegerField(verbose_name='パーオン', blank=True, null=True)
    putt = models.PositiveSmallIntegerField(verbose_name='パット数', blank=True, null=True)

    def __str__(self):
        return f'#{self.pk} {self.player}'