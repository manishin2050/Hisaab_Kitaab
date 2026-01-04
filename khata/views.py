from django.shortcuts import render,redirect
from khata.models import Description,Spilt,EqualShare,EqualShareSplit,Shopping
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from itertools import zip_longest
from django.db import transaction
import time
# from .utils import get_user_balance

import pytz

from django.db.models import Sum,Count,Q


# Create your views here.
from django.http import HttpResponse








rent=7000

asia_tz = pytz.timezone('Asia/Kolkata')




def download(request):

    # Create an Excel file in memory
    if request.method=="POST":

        sdate=request.POST.get('from')
        edate=request.POST.get('to')
        # print(sdate)
        try:
            # start_date = datetime.strptime(f"{sdate}", '%Y-%m-%d').strftime('%m/%d/%y')
            # end_date = datetime.strptime(f"{edate}", '%Y-%m-%d').strftime('%m/%d/%y')
            start_date = sdate
            end_date = edate
        except ValueError:
            return HttpResponse("Invalid date format. Use MM/DD/YY.", status=400)

        descc=Description.objects.filter(date__range=(start_date,end_date)).prefetch_related('spilts').order_by('-id')

        data={

            "objs":descc,
            "date":datetime.now(asia_tz).date(),

        }

        return render(request,"download.html",data)
    else:
        data={
            "date":datetime.now(asia_tz).date(),

        }
        return render(request,"download.html",data)

def home(request):
 
    if User.objects.all().count() > 0:
        today = datetime.now(asia_tz)

    #     # Determine the current month and year
        current_month = today.month
        current_year = today.year

        # Calculate the start and end dates
        if today.day >= 8:  # If today is the 8th or later, filter 8th of this month to 8th of next month
            start_date = datetime(current_year, current_month, 8,tzinfo=asia_tz)
            if current_month == 12:  # Handle year-end transition
                end_date = datetime(current_year + 1, 1,8,tzinfo=asia_tz)
            else:
                end_date = datetime(current_year, current_month + 1, 8,tzinfo=asia_tz)
        else:  # If today is before the 8th, filter 8th of last month to 8th of this month
            if current_month == 1:  # Handle year-start transition
                start_date = datetime(current_year - 1, 12, 8,tzinfo=asia_tz)
            else:
                start_date = datetime(current_year, current_month - 1, 8,tzinfo=asia_tz)
            end_date = datetime(current_year, current_month, 8,tzinfo=asia_tz)

        # Format dates as MM/DD/YY for debugging or display
        formatted_start_date = start_date.strftime('%Y-%m-%d')
        name_start_date=start_date.date()
        formatted_end_date = end_date.strftime('%Y-%m-%d')

        descc=Description.objects.filter(date__range=(formatted_start_date, formatted_end_date)).prefetch_related('spilts').order_by('-id')
        users = User.objects.exclude(id=1)
        online_users = User.objects.exclude(id=1).filter(profile__is_online=True)
      
        rent_per_user = Decimal(rent) / Decimal(len(online_users)) if len(online_users) > 0 else Decimal(1)
        def get_user_balance(user):
            user_expenses = (
                Description.objects
                .filter(date__range=(formatted_start_date, formatted_end_date), payer=user)
                .aggregate(total_amount=Sum('amount'))  # aggregate one number
            )

            spilt_expense = (
                Spilt.objects
                .filter(date__range=(formatted_start_date, formatted_end_date), user=user)
                .aggregate(total_amount=Sum('share'))  # aggregate one number Spilt.objects
            )
            equal_share=(
                EqualShareSplit.objects
                .filter(date__range=(formatted_start_date, formatted_end_date), user=user)
                .aggregate(total_amount=Sum('amount'))  # aggregate one number
            )
           
            credit = user_expenses["total_amount"] or Decimal(0)
            debit = spilt_expense["total_amount"] or Decimal(0)
            sharing = equal_share["total_amount"] or Decimal(0)
          
            if user.profile.is_online:
                user_rent = rent_per_user
            else:
                user_rent = Decimal(0)
            return ( user_rent + debit - credit + sharing).quantize(Decimal('0.01'))
            # return (Decimal(credit) - Decimal(debit)).quantize(Decimal('0.01'))

        balances = []
        for u in users:
            balances.append({
                'user': u,
                'balance': get_user_balance(u)
            })

        # print("this is balance :", balances)
        total_balance = sum(b['balance'] for b in balances)

        data={
                "objs":descc,
                "online_users": zip_longest(users,balances,fillvalue=0),
                "start_date":name_start_date,
                "total_balance":total_balance,
                "rent_per_user":rent_per_user.quantize(Decimal('0.01')),
                "rent_user_count":online_users,
                "today_date":datetime.now().date(),         
        }

        return render(request,"dashboard.html",data)
    else:
        data={
            "date":datetime.now(asia_tz).date(),

        }
        return render(request,"dashboard.html",data)

@login_required(login_url='khata:login')
def add_expense(request):
    if request.method=="POST":
       payer=User.objects.get(id=request.user.id)
       amount=request.POST.get('price')
       desc=request.POST.get('desc')
       date=datetime.now(asia_tz).date()
       times=datetime.now(asia_tz).strftime("%I:%M %p")
       user_list=request.POST.getlist('userss')
    #    print("this is user list: ",payer,amount,desc,date,times,user_list)
       expense=Description.objects.create(payer=payer,amount=amount,description=desc,date=date,times=times)
                        #    users = User.objects.exclude(id=1).filter(profile__is_online=True)

       total_user=len(user_list)

              
       amount = Decimal(amount)
       per_share = (amount / Decimal(total_user)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
       # remainder due to rounding (ex: 100/3)
       remainder = amount - (per_share * total_user)
    #    print("this is reminder: ", remainder)
       with transaction.atomic():
           for u in user_list:
               share = per_share
               # Give remainder to payer (so total shares sum to amount)
               if User.objects.get(id=u) == payer:
                   share = per_share + remainder
            #    print("split:- ",payer,u,share,date,times)    
               Spilt.objects.create(expense=expense, user=User.objects.get(id=u), share=share,date=date,times=times) 
       return redirect('khata:home')
    else:
        return render(request,"add_expense.html")

@login_required
def equalShareSplitor(request):
    if request.method=="POST":
       payer=User.objects.get(id=request.user.id)
       amount=request.POST.get('price')
       desc=request.POST.get('desc')
       date=datetime.now(asia_tz).date()
       times=datetime.now(asia_tz).strftime("%I:%M %p")
       user_list=request.POST.getlist('userss')
    #    print("this is Equal sharelist: ",payer,amount,desc,date,times,user_list)
       expense=EqualShare.objects.create(user=payer,amount=amount,desc=desc,date=date,times=times)
                        #    users = User.objects.exclude(id=1).filter(profile__is_online=True)

       total_user=len(user_list)

              
       amount = Decimal(amount)
       per_share = (amount / Decimal(total_user)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
       # remainder due to rounding (ex: 100/3)
       remainder = amount - (per_share * total_user)
    #    print("this is reminder: ", remainder)
       with transaction.atomic():
           for u in user_list:
               share = per_share
               # Give remainder to payer (so total shares sum to amount)
               if User.objects.get(id=u) == payer:
                   share = per_share + remainder
            #    print("Equalshare split:- ",payer,u,share)    
               EqualShareSplit.objects.create(speaker=expense, user=User.objects.get(id=u), amount=share,date=date,times=times) 
       return redirect('khata:home')

@login_required
def shopping(request):
    if request.method=="POST":
       payer=User.objects.get(id=request.user.id)
       amount=request.POST.get('price')
       desc=request.POST.get('desc')
       date=datetime.now(asia_tz).date()
       times=datetime.now(asia_tz).strftime("%I:%M %p")

    #    print("this is user list: ",payer,amount,desc,date,times)
       expense=Shopping.objects.create(payer=payer,amount=amount,desc=desc,date=date,times=times)
    #    print("this is expense: ",expense)
       return redirect('khata:home')
    
    return render(request,"shopping.html",{"today_date":datetime.now()})

@login_required
def profile(request):

    # 7th to 7th date
    today = datetime.now(asia_tz)
    # Determine the current month and year
    current_month = today.month
    current_year = today.year
    # Calculate the start and end dates
    if today.day >= 8:  # If today is the 8th or later, filter 8th of this month to 8th of next month
        start_date = datetime(current_year, current_month, 8,tzinfo=asia_tz)
        if current_month == 12:  # Handle year-end transition
            end_date = datetime(current_year + 1, 1,8,tzinfo=asia_tz)
        else:
            end_date = datetime(current_year, current_month + 1, 8,tzinfo=asia_tz)
    else:  # If today is before the 8th, filter 8th of last month to 8th of this month
        if current_month == 1:  # Handle year-start transition
            start_date = datetime(current_year - 1, 12, 8,tzinfo=asia_tz)
        else:
            start_date = datetime(current_year, current_month - 1, 8,tzinfo=asia_tz)
        end_date = datetime(current_year, current_month, 8,tzinfo=asia_tz)
    # Format dates as MM/DD/YY for debugging or display
    formatted_start_date = start_date.strftime('%Y-%m-%d')
    formatted_end_date = end_date.strftime('%Y-%m-%d')

    # Total expense by current user
    total_expense = Description.objects.filter(payer=request.user,date__range=(formatted_start_date, formatted_end_date)).aggregate(
        Sum('amount')
    )['amount__sum'] or 0
    #Total Shopping by current user
    total_Shopping_expense = Shopping.objects.filter(payer=request.user,date__range=(formatted_start_date, formatted_end_date)).aggregate(
            Sum('amount')
        )['amount__sum'] or 0

    # Sabhi users ka expense (group by payer)
    all_user_expense = (
    User.objects.annotate(
        balance=Sum(
            "paid_expenses__amount",
            filter=Q(paid_expenses__date__range=(formatted_start_date, formatted_end_date))
        )
    )
    .exclude(id__in=[request.user.id, 1])
)

    # Recent expenses of current user
    recent_expenses = Description.objects.filter(payer=request.user,date__range=(formatted_start_date, formatted_end_date)).prefetch_related('spilts').order_by('-id')

    #Shopping of current user
    shopping_expenses = Shopping.objects.filter(payer=request.user,date__range=(formatted_start_date, formatted_end_date)).order_by('-id')

    #equal share model
    equal_share_expenses = EqualShare.objects.all().prefetch_related('equalsharessplit').order_by('-id')
    return render(request, "profile.html", {
        "total_expense": total_expense,
        "total_Shopping_expense": total_Shopping_expense,
        "all_user_expense": all_user_expense,
        "shopping_expenses": shopping_expenses,
        "equal_share_expenses": equal_share_expenses,
        "recent_expenses": recent_expenses,
    })


def signup_view(request):
    if request.method == "POST":
        username   = request.POST.get('username')
        email      = request.POST.get('email')
        firstname  = request.POST.get('first_name')
        lastname   = request.POST.get('last_name')
        password1  = request.POST.get('password1')
        password2  = request.POST.get('password2')

        # 1️⃣ Check empty fields
        if not all([username, email, firstname, lastname, password1, password2]):
            data = {
                "error": "All fields are required",
                "date": datetime.now(asia_tz).date(),
            }
            return render(request, "signup.html", data)

        # 2️⃣ Passwords match check
        if password1 != password2:
            data = {
                "error": "Passwords do not match",
                "date": datetime.now(asia_tz).date(),
            }
            return render(request, "signup.html", data)

        # 3️⃣ Check if username exists
        if User.objects.filter(username=username).exists():
            data = {
                "error": "Username already taken",
                "date": datetime.now(asia_tz).date(),
            }
            return render(request, "signup.html", data)

        # 4️⃣ Check if email exists
        if User.objects.filter(email=email).exists():
            data = {
                "error": "Email already exists",
                "date": datetime.now(asia_tz).date(),
            }
            return render(request, "signup.html", data)

        # 5️⃣ Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=firstname,
            last_name=lastname
        )
        user.save()
        # print("✅ User created successfully")

        time.sleep(2)  # Optional: just to simulate a delay
        login(request, user)

        return redirect('khata:home')

    else:
        data = {
            "date": datetime.now(asia_tz).date(),
        }
        return render(request, "signup.html", data)

def login_view(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        # print(email,password)
        try:
            user=User.objects.get(email=email)
            # print(user)
            user=authenticate(request,username=user.username,password=password)
            # print("this is user after authenticate: ",user)
            if user is not None:
                login(request,user)
                # print("user is logged in")
                return redirect('khata:home')
            else:
                data={
                    "error":"Invalid email or password",
                    "date":datetime.now(asia_tz).date(),
                }
                return render(request,"login.html",data)
        except User.DoesNotExist:
            data={
                "error":"Invalid email or password",
                "date":datetime.now(asia_tz).date(),
            }
            return render(request,"login.html",data)
    else:
        data={
            "date":datetime.now(asia_tz).date(),
        }
        return render(request,"login.html",data)


def log_out(request):
    if request.method=="POST":
        logout(request)
    return redirect('khata:home')


