from curses.ascii import HT
from datetime import datetime, timedelta
import random
from django.forms import Form
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from .models import Diabetes, Measurement, User, Client, TwoFactorCodes, Vaccine, BloodPressures
from .forms import Bloodpressure, ChangeVaccineStatus, Glucose, LogOut, LoginForm, RegisterForm, TwoFactor, Vaccines, Weight
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator


def generateRandomCode() -> int:
    random_number = random.randint(1000, 9999)
    return random_number


def validateLogin(request) -> bool:
    if(len(request.session.get('user_email', '')) < 1):
        return False
    return True


def validateLoginTwoFA(request) -> bool:
    if(len(request.session.get('user_email', '')) < 1):
        return False
    if(request.session.get('twofa', False)):
        return True

def getSessionClient(request) -> Client:
    foundClient = Client.objects.filter(email = request.session['user_email'])
    return foundClient[0]

def getSessionUser(request) -> User:
    foundUser = User.objects.filter(email = request.session['user_email'])
    return foundUser[0]



def index(request):
    if(not validateLoginTwoFA(request)):
        return render(request, 'index.html', {'logged_in': False})
    return render(request, 'index.html', {'logged_in': True})


def login(request):
    if validateLoginTwoFA(request):
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if(form.is_valid()):
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            foundUser = User.objects.filter(email=email)
            if(len(foundUser) < 1):
                form.add_error('email', 'Usuário ou senha inválidos!')
                form.add_error('password', 'Usuário ou senha inválidos!')
                return render(request, 'login.html', {'form': form})
            if(foundUser[0].password == password):
                exp_date = (datetime.utcnow() - timedelta(hours=3)
                            ) + timedelta(hours=12)
                code = generateRandomCode()
                twoFA = TwoFactorCodes(
                    code=code, exp_date=exp_date, user=foundUser[0])
                twoFA.save()
                send_mail(
                    'Conexão Saúde - Código de confirmação',
                    f'Quando pedido, insira o seguinte código: {code}\nVálido até: {datetime.strftime(exp_date, "%d/%m/%Y %H:%M:%S")}',
                    'conexaosaude@techconnect.com.br',
                    [email],
                    fail_silently=False,
                )
                request.session['user_email'] = email
                request.session['twofa'] = False
                return HttpResponseRedirect('/twofactor')
            else:
                form.add_error('email', 'Usuário ou senha inválidos!')
                form.add_error('password', 'Usuário ou senha inválidos!')
                return render(request, 'login.html', {'form': form})

    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def twoFactor(request):
    if(validateLoginTwoFA(request)):
        return HttpResponseRedirect('/user')
    if not validateLogin(request):
        return HttpResponseRedirect('/login')
    if(request.method == 'POST'):
        form = TwoFactor(request.POST)
        if(form.is_valid()):
            code = form.cleaned_data['code']
            user = getSessionUser(request)
            date = datetime.utcnow() - timedelta(hours=3)
            foundCodes = TwoFactorCodes.objects.filter(
                user=user, exp_date__gte=date)
            if(len(foundCodes) < 1):
                form.add_error('code', 'Código inválido.')
                return render(request, 'twofactor.html', {'form': form, 'logged_in': True})
            for foundCode in foundCodes:
                if foundCode.code == code:
                    request.session['twofa'] = True
                    return HttpResponseRedirect('/user')
            form.add_error('code', 'Código inválido.')
            return render(request, 'twofactor.html', {'form': form, 'logged_in': True})
    else:
        form = TwoFactor()
    return render(request, 'twofactor.html', {'form': form, 'logged_in': True})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if(form.is_valid()):
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            date = form.cleaned_data['date']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']
            cpf = form.cleaned_data['cpf']
            foundUserByEmail = User.objects.filter(email=email)
            foundUserByCpf = Client.objects.filter(cpf=cpf)
            if(len(foundUserByEmail) > 0):
                form.add_error('email', 'Email já em uso.')
                return render(request, 'register.html', {'form': form})
            elif(len(foundUserByCpf) > 0):
                form.add_error('cpf', 'CPF já em uso.')
                return render(request, 'register.html', {'form': form})
            user = User(email=email, password=password)
            user.save()
            client = Client(name=name, email=email, date=date,
                            user=user, phone=phone, cpf=cpf)
            client.save()
            return HttpResponseRedirect('/login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def newcode(request):
    if(not validateLogin(request)):
        return HttpResponseRedirect('/login')
    if request.method == 'POST':
        user = getSessionUser[request]
        exp_date = (datetime.utcnow() - timedelta(hours=3)) + \
            timedelta(hours=12)
        code = generateRandomCode()
        twoFA = TwoFactorCodes(code=code, exp_date=exp_date, user=user)
        twoFA.save()
        send_mail(
            'Conexão Saúde - Código de confirmação',
            f'Quando pedido, insira o seguinte código: {code}\nVálido até: {datetime.strftime(exp_date, "%d/%m/%Y %H:%M:%S")}',
            'conexaosaude@techconnect.com.br',
            [request.session['user_email']],
            fail_silently=False,
        )
        return HttpResponseRedirect('/twofactor')
    else:
        return HttpResponseRedirect('/login')


def logout(request):
    request.session['user_email'] = ''
    return HttpResponseRedirect('/')


def user(request):
    if(not validateLoginTwoFA(request)):
        return HttpResponseRedirect('/login')
    form = LogOut()
    return render(request, 'user.html', {'form': form})

def weight(request):
    if(not validateLoginTwoFA(request)):
        return HttpResponseRedirect('/login')
    client = getSessionClient(request)
    weight_registers = Measurement.objects.filter(client=client).order_by('-register_date')
    weight_paginator = Paginator(weight_registers, 10)
    page_number = request.GET.get('page')
    if(page_number is None):
        page_number = 1
    page_obj = weight_paginator.get_page(page_number)
    page_obj.adjusted_elided_pages = weight_paginator.get_elided_page_range(page_number)
    if(request.method == 'POST'):
        form = Weight(request.POST)
        if(form.is_valid()):
            note = form.cleaned_data['note']
            weight = form.cleaned_data['weight']
            height = form.cleaned_data['height']
            client = getSessionClient(request)
            imc = round(weight / (height * height), 2)
            measurement = Measurement(note = note, weight = weight, height = height, register_date = datetime.utcnow() - timedelta(hours=3), client = client, imc = imc)
            measurement.save()
            messages.success(request, 'Registro incluído com sucesso!')
            return HttpResponseRedirect('/weight')
    form = Weight()
    return render(request, 'weight.html', {'form': form, 'page_obj': page_obj})


def vaccines(request):
    if(not validateLoginTwoFA(request)):
        return HttpResponseRedirect('/login')
    client = getSessionClient(request)
    vaccine_registers = Vaccine.objects.filter(client=client).order_by('-register_date')
    vaccine_paginator = Paginator(vaccine_registers, 10)
    page_number = request.GET.get('page')
    if(page_number is None):
        page_number = 1
    page_obj = vaccine_paginator.get_page(page_number)
    page_obj.adjusted_elided_pages = vaccine_paginator.get_elided_page_range(page_number)
    if(request.method == 'POST'):
        form = Vaccines(request.POST)
        if(form.is_valid()):
            aplication_date = form.cleaned_data['application_date']
            note = form.cleaned_data['note']
            vaccine_name = form.cleaned_data['vaccine_name']
            aplicated = form.cleaned_data['aplicated']
            client = getSessionClient(request)
            vaccine_register = Vaccine(
                vaccine_name = vaccine_name,
                register_date = datetime.utcnow() - timedelta(hours=3),
                note = note,
                client = client,
                aplication_date = aplication_date,
                aplicated = aplicated
            )
            vaccine_register.save()
            messages.success(request, 'Registro incluído com sucesso!')
            return HttpResponseRedirect('/vaccines')
    form = Vaccines()
    changevaccine = ChangeVaccineStatus()
    return render(request, 'vaccines.html', {'form': form, 'page_obj': page_obj, 'changevaccine': changevaccine})

def changevaccinestatus(request):
    if(request.method == 'POST'):
        form = ChangeVaccineStatus(request.POST)
        if(form.is_valid()):
            new_status = form.cleaned_data['new_status']
            id = form.data.get('id')
            vaccine_register = Vaccine.objects.filter(id = id)[0]
            if(vaccine_register.aplicated != new_status):
                vaccine_register.aplicated = new_status
                vaccine_register.save()      
    return HttpResponseRedirect('/vaccines')

def glucose(request):
    if(not validateLoginTwoFA(request)):
        return HttpResponseRedirect('/login')
    client = getSessionClient(request)
    glucose_registers = Diabetes.objects.filter(client=client).order_by('-register_date')
    glucose_paginator = Paginator(glucose_registers, 10)
    page_number = request.GET.get('page')
    if(page_number is None):
        page_number = 1
    page_obj = glucose_paginator.get_page(page_number)
    page_obj.adjusted_elided_pages = glucose_paginator.get_elided_page_range(page_number)
    if(request.method == 'POST'):
        form = Glucose(request.POST)
        if(form.is_valid()):
            note = form.cleaned_data['note']
            registered_value = form.cleaned_data['registered_value']
            client = getSessionClient(request)
            glucose_register = Diabetes(note = note, registered_value = registered_value, client = client, register_date = datetime.utcnow() - timedelta(hours=3))
            glucose_register.save()
            messages.success(request, 'Registro incluído com sucesso!')
            return HttpResponseRedirect('/glucose')
    form = Glucose()
    return render(request, 'glucose.html', {'form': form, 'page_obj': page_obj})

def bloodpressure(request):
    if(not validateLoginTwoFA(request)):
        return HttpResponseRedirect('/login')
    client = getSessionClient(request)
    bloodpressure_registers = BloodPressures.objects.filter(client=client).order_by('-register_date')
    bloodpressure_paginator = Paginator(bloodpressure_registers, 10)
    page_number = request.GET.get('page')
    if(page_number is None):
        page_number = 1
    page_obj = bloodpressure_paginator.get_page(page_number)
    page_obj.adjusted_elided_pages = bloodpressure_paginator.get_elided_page_range(page_number)
    if(request.method == 'POST'):
        form = Bloodpressure(request.POST)
        if(form.is_valid()):
            note = form.cleaned_data['note']
            pa_sistolica = form.cleaned_data['pa_sistolica']
            pa_diastolica = form.cleaned_data['pa_diastolica']
            calculo_pressao = round(((pa_sistolica * 10) + (2 * (pa_diastolica * 10))) / 3, 2)
            client = getSessionClient(request)
            bloodpressure_register = BloodPressures(note = note, pa_sistolica = pa_sistolica, pa_diastolica = pa_diastolica, calculo_pressao = calculo_pressao, client = client, register_date = datetime.utcnow() - timedelta(hours=3))
            bloodpressure_register.save()
            messages.success(request, 'Registro incluído com sucesso!')
            return HttpResponseRedirect('/bloodpressure')
    form = Bloodpressure()
    return render(request, 'bloodpressure.html', {'form': form, 'page_obj': page_obj})
