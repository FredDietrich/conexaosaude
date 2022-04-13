from cProfile import label
import datetime
from django import forms
from django.conf import settings

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150, label="Nome completo")
    date = forms.DateField(widget=forms.SelectDateWidget(
        years=range(datetime.date.today().year, 1900, -1)
    ), label="Data de nascimento")
    email = forms.EmailField(max_length=15, widget=forms.EmailInput(attrs={'onkeyup': 'validateEmail(this.value)'}), label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, max_length=20, label="Senha")

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150, label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, max_length=20, label="Senha")
    
class TwoFactor(forms.Form):
    code = forms.DecimalField(max_value=9999, min_value=1000)

class Forgot(forms.Form):
    email = forms.EmailField(max_length=150)
    date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

class NewCode(forms.Form):
    None

class LogOut(forms.Form):
    None