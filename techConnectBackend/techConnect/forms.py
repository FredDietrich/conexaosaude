from django import forms
from django.conf import settings

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150)
    date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    email = forms.EmailField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, max_length=20)

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, max_length=20)
    
class TwoFactor(forms.Form):
    code = forms.DecimalField(max_value=9999, min_value=1000)

class Forgot(forms.Form):
    email = forms.EmailField(max_length=150)
    date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

class NewCode(forms.Form):
    None

class LogOut(forms.Form):
    None
