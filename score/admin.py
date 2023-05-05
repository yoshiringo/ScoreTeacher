from django.contrib import admin
from .models import Person, Stat

# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name']

class StatAdmin(admin.ModelAdmin):
    list_display = ['player','date', 'total_score', 'ob', 'penalty', 'fw', 'par_on', 'putt']


admin.site.register(Person, PersonAdmin)
admin.site.register(Stat, StatAdmin)