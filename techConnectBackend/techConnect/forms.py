from cProfile import label
import datetime
from django import forms
from django.conf import settings

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150, label="Nome completo")
    date = forms.DateField(widget=forms.SelectDateWidget(
        years=range(datetime.date.today().year, 1900, -1)
    ), label="Data de nascimento")
    email = forms.EmailField(max_length=150, widget=forms.EmailInput(attrs={'onkeyup': 'validateEmail(this.value)'}), label="E-mail")
    phone = forms.CharField(max_length=15, label="Celular")
    cpf = forms.CharField(max_length=15, label='CPF')
    password = forms.CharField(widget=forms.PasswordInput, max_length=20, label="Senha")

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150, label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, max_length=20, label="Senha")
    
class TwoFactor(forms.Form):
    code = forms.DecimalField(max_value=9999, min_value=1000, label="Código")

class Forgot(forms.Form):
    email = forms.EmailField(max_length=150)
    date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

class NewCode(forms.Form):
    None

class LogOut(forms.Form):
    None

class Bloodpressure(forms.Form):
    note = forms.CharField(max_length=150)
    registered_value = forms.DecimalField()

class Glucose(forms.Form):
    note = forms.CharField(max_length=150)
    registered_value = forms.DecimalField()
    
class Weight(forms.Form):
    note = forms.CharField(max_length=150, label="Nota")
    weight = forms.DecimalField(max_value=999, label="Peso (kg)")
    height = forms.DecimalField(max_value=999, label="Altura (cm)")

class Vaccines(forms.Form):
    title = forms.CharField(max_length=150)
    expected_date = forms.DateField()
    applied_date = forms.DateTimeField()    
    