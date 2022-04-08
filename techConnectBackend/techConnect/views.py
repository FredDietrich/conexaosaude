from curses.ascii import HT
from datetime import datetime, timedelta
import random
from django.shortcuts import render
from django.core.mail import send_mail

from .models import User, Client, TwoFactorCodes
from .forms import Forgot, LoginForm, RegisterForm, TwoFactor
from django.http import HttpResponseRedirect

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
    if(validateLogin(request) or validateLoginTwoFA(request)):
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if(form.is_valid()):
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            foundUser = User.objects.filter(email = email)
            if(len(foundUser) < 1):
                return render(request, 'login.html', {'form': form, 'invalidUserOrPassword': True})
            if(foundUser[0].password == password):
                exp_date = (datetime.utcnow() - timedelta(hours=3)) + timedelta(hours=12)
                code = generateRandomCode()
                twoFA = TwoFactorCodes(code = code, exp_date = exp_date, user = foundUser[0])
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
                return render(request, 'login.html', {'form': form, 'invalidUserOrPassword': True})

    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def twoFactor(request):
    if(validateLoginTwoFA(request)):
        return HttpResponseRedirect('/')
    if not validateLogin(request):
        return render(request, 'twofactor.html', {'invalid_code': False, 'logged_in': False})
    if(request.method == 'POST'):
        form = TwoFactor(request.POST)
        if(form.is_valid()):
            code = form.cleaned_data['code']
            foundUser = User.objects.filter(email = request.session['user_email'])
            date = datetime.utcnow() - timedelta(hours=3)
            foundCodes = TwoFactorCodes.objects.filter(user = foundUser[0], exp_date__gte = date)
            if(len(foundCodes) < 1):
                return render(request, 'twofactor.html', {'form': form, 'invalid_code': True, 'logged_in': True})
            for foundCode in foundCodes:
                if foundCode.code == code:
                    request.session['twofa'] = True
                    return HttpResponseRedirect('/')
            return render(request, 'twofactor.html', {'form': form, 'invalid_code': True, 'logged_in': True})
    else:
        form = TwoFactor()
    return render(request, 'twofactor.html', {'form':form, 'invalid_code': False, 'logged_in': True})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if(form.is_valid()):
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            date = form.cleaned_data['date']
            password = form.cleaned_data['password']
            user = User(email = email, password = password)
            user.save()
            client = Client(name = name, email = email, date = date, user = user)
            client.save()
            return HttpResponseRedirect('/login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def newcode(request):
    if(not validateLogin(request)):
        return HttpResponseRedirect('/login')
    if request.method == 'POST':
        foundUser = User.objects.filter(email = request.session['user_email'])
        exp_date = (datetime.utcnow() - timedelta(hours=3)) + timedelta(hours=12)
        code = generateRandomCode()
        twoFA = TwoFactorCodes(code = code, exp_date = exp_date, user = foundUser[0])
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