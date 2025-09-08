from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, ROUND_DOWN

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_online = models.BooleanField(default=False)   # user login hai ya nahi
    last_seen = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.user.username

class Description(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_expenses',default=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    description = models.CharField(max_length=255, blank=True)
    date=models.DateField(null=True)
    times=models.CharField(null=True,max_length=50)

    def __str__(self):
        return f"{self.description} - {self.amount} by {self.payer.username}"


class Spilt(models.Model):
    expense= models.ForeignKey(Description, on_delete=models.CASCADE, related_name='spilts',default=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spilts',default=2)
    share = models.DecimalField(max_digits=10, decimal_places=2)
    date=models.DateField(null=True)
    times=models.CharField(null=True,max_length=50)
    def __str__(self):
        return f"{self.user} owes {self.share}rs for {self.expense.id} " 

class Shopping(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shoppings',default=2)
    amount=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    desc=models.CharField(max_length=255, blank=True)
    date=models.DateField(null=True)
    times=models.CharField(null=True,max_length=50)
    def __str__(self):
        return f"{self.payer} shop {self.desc}"

class EqualShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equalshares',default=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    desc=models.CharField(max_length=255, blank=True)
    date=models.DateField(null=True)
    times=models.CharField(null=True,max_length=50)
    def __str__(self):
        return f"{self.user} added {self.desc}"
    
class EqualShareSplit(models.Model):
    speaker=models.ForeignKey(EqualShare,on_delete=models.CASCADE,related_name='equalsharessplit')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equalsharessplit',default=2)
    amount= models.DecimalField(max_digits=10, decimal_places=2,default=0)
    date=models.DateField(null=True)
    times=models.CharField(null=True,max_length=50)
    def __str__(self):
        return f"{self.speaker} ka hissa {self.amount}"
    
