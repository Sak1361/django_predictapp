from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django import forms


class FileInputWithPreview(forms.ClearableFileInput):
    """プレビュー表示されるinput type=file"""
    template_name = 'predictions/widgets/file_input_with_preview.html'

    class Media:
        js = ['predictions/js/preview.js']

    def __init__(self, attrs=None, include_preview=False):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += 'preview-marker'
        else:
            self.attrs['class'] = 'preview-marker'
        self.include_preview = include_preview

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'include_preview': self.include_preview,
        })
        return context


class Photo_form(forms.Form):
    image = forms.ImageField(widget=FileInputWithPreview())

    # image = forms.ImageField(widget=forms.FileInput(
    #    attrs={'class': 'custom-file-input'}))


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
