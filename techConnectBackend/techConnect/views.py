from curses.ascii import HT
from datetime import datetime, timedelta
import random
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from .models import Measurement, User, Client, TwoFactorCodes, Vaccine
from .forms import Forgot, LoginForm, RegisterForm, TwoFactor, Weight
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator


def generateRandomCode():
    random_number = random.randint(1000, 9999)
    return random_number


def validateLogin(request):
    if(len(request.session.get('user_email', '')) < 1):
        return False
    return True


def validateLoginTwoFA(request):
    if(len(request.session.get('user_email', '')) < 1):
        return False
    if(request.session.get('twofa', False)):
        return True


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
        return render(request, 'twofactor.html', {'invalid_code': False, 'logged_in': False})
    if(request.method == 'POST'):
        form = TwoFactor(request.POST)
        if(form.is_valid()):
            code = form.cleaned_data['code']
            foundUser = User.objects.filter(
                email=request.session['user_email'])
            date = datetime.utcnow() - timedelta(hours=3)
            foundCodes = TwoFactorCodes.objects.filter(
                user=foundUser[0], exp_date__gte=date)
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
        foundUser = User.objects.filter(email=request.session['user_email'])
        exp_date = (datetime.utcnow() - timedelta(hours=3)) + \
            timedelta(hours=12)
        code = generateRandomCode()
        twoFA = TwoFactorCodes(code=code, exp_date=exp_date, user=foundUser[0])
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
    return render(request, 'user.html')


def bloodpressure(request):
    pass


def weight(request):
    if(not validateLoginTwoFA(request)):
        return HttpResponseRedirect('/login')
    client = Client.objects.filter(email=request.session['user_email'])
    weight_registers = Measurement.objects.filter(client=client[0])
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
            client = Client.objects.filter(email=request.session['user_email'])
            measurement = Measurement(note = note, weight = weight, height = height, register_date = datetime.utcnow() - timedelta(hours=3), client = client[0])
            measurement.save()
            messages.success(request, 'Registro incluído com sucesso!')
            return render(request, 'weight.html', {'form': form, 'page_obj': page_obj})
    form = Weight()
    return render(request, 'weight.html', {'form': form, 'page_obj': page_obj})


def vaccines(request):
    if(not validateLoginTwoFA(request)):
        return HttpResponseRedirect('/login')
    if(request.method == 'POST'):
        form = Vaccine(request.POST)
        # if

    return render(request, 'vaccines.html')


def glucose(request):
    pass
