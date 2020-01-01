from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django import forms


class Photo_form(forms.Form):
    image = forms.ImageField(widget=forms.FileInput(
        attrs={'class': 'custom-file-input'}))


User = get_user_model()


class User_update_form(forms.ModelForm):
    # ユーザー情報更新フォーム
    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class Login_form(AuthenticationForm):
    # ログインフォーム
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class User_create_form(UserCreationForm):
    # ユーザー登録用フォーム
    email = forms.EmailField(required=True)  # メールも必須に

    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        # 再登録時にメアドがかぶらないように
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email
