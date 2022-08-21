from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Hasla musza byc identyczne')
        return cd['password2']

    def validate(self):
        password1 = self.cleaned_data['password1']
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}:;'\[\]]"

        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError('Password must contain at least %(min_length)d digit.')
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError('Password must contain at least %(min_length)d letter.')
        if not any(char in special_characters for char in password1):
            raise forms.ValidationError('haslo musi zawierac znaki specjalne')

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


