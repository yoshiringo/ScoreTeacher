
from django import forms
from .models import Stat, Person
import csv
import io

class StatCreateForm(forms.ModelForm):
    class Meta:
        model = Stat
        exclude = ('player','stat_number')
        widgets = {
            'date': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': 'ラウンド日',
                                                 'class': 'form-control'}),
            'total_score': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': 'スコア',
                                                  'class': 'form-control'}),
            'ob': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': 'OB数',
                                                  'class': 'form-control'}),
            'penalty': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': 'ペナルティ率',
                                                  'class': 'form-control'}),
            'fw': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': 'FWキープ率',
                                                  'class': 'form-control'}),
            'par_on': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': 'パーオン率',
                                                  'class': 'form-control'}),
            'putt': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': 'パット数',
                                                  'class': 'form-control'}),
            'bunker': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': 'バンカー数',
                                                  'class': 'form-control'}),                                                                                                                                                          
        }

class PersonCreateForm(forms.ModelForm):
    class Meta:
        model = Person
        
        fields = ["name", "sex", "age"]
        labels = {
            'name' : '名前',
            'age' : '年齢'
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["autocomplete"] = "off"

class CSVUploadForm(forms.Form):
    file = forms.FileField(label='CSVファイル')
