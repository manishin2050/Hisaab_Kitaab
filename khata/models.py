from django.db import models

# Create your models here.
class Manish(models.Model):
    date=models.DateField(null=True)
    price=models.FloatField(null=True)
    checkbox=models.CharField(null=True,max_length=5)
    discount=models.FloatField(null=True,default=0)
    times=models.CharField(null=True,max_length=50)

class Kazim(models.Model):
    date=models.DateField(null=True)
    price=models.FloatField(null=True)
    checkbox=models.CharField(null=True,max_length=5)
    discount=models.FloatField(null=True)
    times=models.CharField(null=True,max_length=50)

class Samay(models.Model):
    date=models.DateField(null=True)
    price=models.FloatField(null=True)
    checkbox=models.CharField(null=True,max_length=5)
    discount=models.FloatField(null=True)
    times=models.CharField(null=True,max_length=50)

class Description(models.Model):
    date=models.DateField(null=True)
    desc=models.TextField(null=True)
    paymentby=models.CharField(null=True,max_length=50)
    times=models.CharField(null=True,max_length=50)


class Manish_Khata(models.Model):
    date=models.DateField(null=True)
    price=models.FloatField(null=True)
    desc=models.TextField(null=True)
    times=models.CharField(null=True,max_length=50)
