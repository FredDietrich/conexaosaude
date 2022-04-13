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
    phone = models.CharField(max_length=50)
    cpf = models.CharField(max_length=11)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Vaccine(models.Model):
    title = models.CharField(max_length=150)
    expected_date = models.DateField()
    applied_date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

class Diabetes(models.Model):
    note = models.CharField(max_length=150)
    registered_value = models.FloatField()
    register_date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

class Measurement(models.Model):
    note = models.CharField(max_length=150)
    weight = models.FloatField()
    height = models.FloatField()
    register_date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

class BloodPressure(models.Model):
    note = models.CharField(max_length=150)
    registered_value = models.FloatField()
    register_date = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)