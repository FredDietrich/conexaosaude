from cProfile import label
import datetime
from django import forms
from django.conf import settings


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150, label="Nome completo")
    date = forms.DateField(
        initial=datetime.datetime.now().strftime('%Y-%m-%d'),
        widget=forms.SelectDateWidget(
            years=range(datetime.date.today().year, 1900, -1)
        ), label="Data de nascimento")
    email = forms.EmailField(max_length=150, label="E-mail")
    phone = forms.CharField(max_length=15, label="Celular")
    cpf = forms.CharField(max_length=15, label='CPF')
    password = forms.CharField(
        widget=forms.PasswordInput, max_length=20, label="Senha")


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150, label="E-mail")
    password = forms.CharField(
        widget=forms.PasswordInput, max_length=20, label="Senha")


class TwoFactor(forms.Form):
    code = forms.DecimalField(max_value=9999, min_value=1000, label="Código")


class NewCode(forms.Form):
    None


class LogOut(forms.Form):
    None


class Bloodpressure(forms.Form):
    note = forms.CharField(max_length=50, label="Descrição do registro")
    pa_sistolica = forms.DecimalField(label="PA sistólica", widget=forms.TextInput(attrs={'class': 'form-control'}))
    pa_diastolica = forms.DecimalField(label="PA diastólica", widget=forms.TextInput(attrs={'class': 'form-control'}))


class Glucose(forms.Form):
    note = forms.CharField(max_length=150, label="Descrição do registro")
    registered_value = forms.DecimalField(label="Valor registrado (mg/dl)")


class Weight(forms.Form):
    note = forms.CharField(max_length=150, label="Descrição do registro")
    weight = forms.DecimalField(max_value=999, label="Peso (kg)")
    height = forms.DecimalField(max_value=999, label="Altura (m)")


class Vaccines(forms.Form):
    note = forms.CharField(max_length=50, label="Descrição do registro")
    vaccine_name = forms.CharField(max_length=20, label="Nome da vacina")
    application_date = forms.DateField(initial=datetime.datetime.now().strftime('%Y-%m-%d'),
                                       widget=forms.SelectDateWidget(
                                           years=range(
                                               datetime.date.today().year + 10, 1900, -1),
    ), label="Data de aplicação")
    aplicated = forms.BooleanField(
        required=False, initial=False, label="Aplicada? (marque caso já tenha feito, e deixe desmarcado caso esteja cadastrando uma vacina futura")


class ChangeVaccineStatus(forms.Form):
    new_status = forms.BooleanField(required=False, initial=False)
