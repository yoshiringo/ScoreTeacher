from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class AccountForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(attrs={'pattern':'^[A-Za-z0-9]+$'}),label="パスワード")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'pattern':'^[A-Za-z0-9]{8,24}$'}),label="パスワード(確認用)")

    def clean_password(self):
        password = self.cleaned_data['password']
        return password
 
    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        return confirm_password
 
    def clean(self):
        cleaned_data = super().clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error(
                field='confirm_password',
                error=ValidationError('パスワードが一致しません。'))
        return cleaned_data

    class Meta():
        # ユーザー認証
        model = User
        # フィールド指定
        fields = ('username','password')
        # フィールド名指定
        labels = {'username':"ユーザーID"}
        widgets =   {
            'username': forms.TextInput(),
        }