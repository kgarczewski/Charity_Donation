from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from charitydonation.models import Donation


class SignUpForm(UserCreationForm):
    username = forms.EmailField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['password1'].label = 'Hasło'
        self.fields['password2'].label = 'Powtórz hasło'

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Uzytkownik o takim mailu istnieje')
        return username

    def clean_password2(self):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}:;'\[\]]"
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Hasla musza byc identyczne! Rozumiesz?')
        if not any(char.isdigit() for char in cd['password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna cyfre')
        if not any(char.isalpha() for char in cd['password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna litere')
        if not any(char.isupper() for char in cd['password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna wielka litere')
        if not any(char in special_characters for char in cd['password1']):
            raise forms.ValidationError('Haslo musi zawierac znaki specjalne')
        return cd['password2']

    # def validate(self):
    #     cd = self.cleaned_data
    #     special_characters = "[~\!@#\$%\^&\*\(\)_\+{}:;'\[\]]"
    #
    #     if not any(char.isdigit() for char in cd['password1']):
    #         raise forms.ValidationError('Password must contain at least %(min_length)d digit.')
    #     if not any(char.isalpha() for char in cd['password1']):
    #         raise forms.ValidationError('Password must contain at least %(min_length)d letter.')
    #     if not any(char in special_characters for char in cd['password2']):
    #         raise forms.ValidationError('haslo musi zawierac znaki specjalne')
    #     return cd['password2']

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class UpdateUserForm(forms.ModelForm):
    username = forms.EmailField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}:;'\[\]]"
        cd = self.cleaned_data
        if cd['new_password1'] != cd['new_password2']:
            raise forms.ValidationError('Hasla musza byc identyczne!')
        if not any(char.isdigit() for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna cyfre')
        if not any(char.isalpha() for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna litere')
        if not any(char.isupper() for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna wielka litere')
        if not any(char in special_characters for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac znaki specjalne')
        return cd['new_password2']


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Stare Hasło'
        self.fields['new_password1'].label = 'Hasło'
        self.fields['new_password2'].label = 'Powtórz hasło'

    def clean_password(self):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}:;'\[\]]"
        cd = super(PasswordChangingForm, self).clean()
        if cd['new_password1'] != cd['new_password2']:
            raise forms.ValidationError('Hasla musza byc identyczne!')
        if not any(char.isdigit() for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna cyfre')
        if not any(char.isalpha() for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna litere')
        if not any(char.isupper() for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac co najmniej jedna wielka litere')
        if not any(char in special_characters for char in cd['new_password1']):
            raise forms.ValidationError('Haslo musi zawierac znaki specjalne')
        return cd['new_password2']

