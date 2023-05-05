from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser

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
    sex = models.CharField(verbose_name="性別", choices=settings.SEX, max_length=2)
    age = models.IntegerField(null=True,blank=True,validators=[MinValueValidator(1)])
    player_number = models.IntegerField(null=True,blank=True)
    
class Stat(models.Model):
    player = models.ForeignKey(to=Person, verbose_name='プレイヤー', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='日付', blank=False, null=False)
    total_score = models.PositiveSmallIntegerField(verbose_name='スコア', blank=False, null=False)
    putt = models.PositiveSmallIntegerField(verbose_name='パット数', blank=False, null=False)
    fw = models.PositiveSmallIntegerField(verbose_name='FWキープ率', blank=False, null=False)
    par_on = models.PositiveSmallIntegerField(verbose_name='パーオン率', blank=False, null=False)
    ob = models.PositiveSmallIntegerField(verbose_name='OB', blank=False, null=False)
    bunker = models.PositiveSmallIntegerField(verbose_name='バンカー数', blank=False, null=False)
    penalty = models.PositiveSmallIntegerField(verbose_name='ペナルティ率', blank=False, null=False)
    stat_number = models.BigIntegerField(null=True)

    def __str__(self):
        return f'#{self.pk} {self.player}'

