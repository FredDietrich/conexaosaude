from django.db import models

class User(models.Model):
    email = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=20)

class TwoFactorCodes(models.Model):
    code = models.IntegerField()
    exp_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Client(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    