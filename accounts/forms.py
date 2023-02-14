from django import forms
from django.contrib.auth.models import User
from .models import Account
from django.core.exceptions import ValidationError

class AccountForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'パスワード', 'pattern':'^[A-Za-z0-9]+$'}),label="パスワード")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'パスワード(確認用)', 'pattern':'^[A-Za-z0-9]{8,24}$'}),label="パスワード(確認用)")

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
        fields = ('username','email','password')
        # フィールド名指定
        labels = {'username':"ユーザーID",'email':"メール"}
        widgets =   {
            'username': forms.TextInput(attrs={'placeholder' : 'ユーザー名'}),
        }

class AddAccountForm(forms.ModelForm):
    class Meta():
        # モデルクラスを指定
        model = Account
        fields = ('last_name','first_name','account_image',)
        labels = {'last_name':"苗字",'first_name':"名前",'account_image':"写真アップロード",}