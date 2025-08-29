from django.shortcuts import render
from khata.models import Manish,Kazim,Samay,Description,Manish_Khata
from datetime import datetime

import pytz

from django.db.models import Sum,Count


# Create your views here.
from django.http import HttpResponse
from openpyxl import Workbook

rent=2333.33

asia_tz = pytz.timezone('Asia/Kolkata')
def download_excel(request):
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
        manish=Manish.objects.filter(date__range=(start_date,end_date))
        kazim=Kazim.objects.filter(date__range=(start_date,end_date))
        samay=Samay.objects.filter(date__range=(start_date,end_date))
        descc=Description.objects.filter(date__range=(start_date,end_date))

        total_manish = format(Manish.objects.filter(date__range=(start_date,end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")
        total_kazim = format(Kazim.objects.filter(date__range=(start_date,end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")
        total_samay = format(Samay.objects.filter(date__range=(start_date,end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")

        discount_manish = format(Manish.objects.filter(date__range=(start_date,end_date)).aggregate(Sum('discount'))['discount__sum']  or 0.0, ".2f")
        discount_kazim = format(Kazim.objects.filter(date__range=(start_date,end_date)).aggregate(Sum('discount'))['discount__sum']  or 0.0, ".2f")
        discount_samay = format(Samay.objects.filter(date__range=(start_date,end_date)).aggregate(Sum('discount'))['discount__sum']  or 0.0, ".2f")



        manish_total= rent + float(total_manish) - float(discount_manish)
        manish_total=format(manish_total,".2f")
        # print(total_manish)
        # print(manish_total)
        # print(discount_manish)
        # print()

        kazim_total= rent + float(total_kazim) - float(discount_kazim)
        kazim_total=format(kazim_total ,".2f")
        # print(total_kazim)
        # print(kazim_total)
        # print(discount_kazim)

        # print()
        samay_total= rent + float(total_samay) - float(discount_samay)
        samay_total=format(samay_total ,".2f")
        # for i in manish:
        #     print(i.price)


        data={
            "obj":zip(manish,kazim,samay,descc),
            "objs":zip(manish,kazim,samay,descc),
            "date":datetime.now(asia_tz).date(),

            "total_manish":total_manish,
            "total_kazim":total_kazim,
            "total_samay":total_samay,

            "discount_manish":discount_manish,
            "discount_kazim":discount_kazim,
            "discount_samay":discount_samay,

            "manish_total": manish_total,
            "kazim_total": kazim_total,
            "samay_total": samay_total,
            "total":format(float(manish_total)+float(kazim_total)+float(samay_total),".2f")
        }

        return render(request,"index.html",data)
    else:
        data={
            "date":datetime.now(asia_tz).date(),

        }
        return render(request,"index.html",data)

def home(request):
    if request.method=="POST":
        price=request.POST.get('price')
        desc=request.POST.get('desc')
        get1=request.POST.get('gett1')
        get3=request.POST.get('gett3')
        get2=request.POST.get('gett2')
        paymentby=request.POST.get('paymentby')
        date=datetime.now(asia_tz).date()
        # price=int(price)/3
        # print(price)
        if get1 == "yes":
            Manish.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price=format((int(price) - (int(price)/3) *2),".2f"),checkbox=get1,discount=(( format((int(price)/3) *2,".2f"))))
            Kazim.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price= str(format( int(price)/3,".2f")) ,checkbox=get2)
            Samay.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price= str(format( int(price)/3,".2f")),checkbox=get3)
        if get2 == "yes":
            Kazim.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price=format((int(price) - (int(price)/3) *2),".2f"),checkbox=get2,discount=(( format((int(price)/3) *2,".2f"))))
            Manish.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price= str(format( int(price)/3,".2f")) ,checkbox=get1)
            Samay.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price= str(format( int(price)/3,".2f")),checkbox=get3)
        if get3 == "yes":
            Samay.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price=format((int(price) - (int(price)/3) *2),".2f"),checkbox=get3,discount=(( format((int(price)/3) *2,".2f"))))
            Kazim.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price= str(format( int(price)/3,".2f")) ,checkbox=get2)
            Manish.objects.create(date=date,times=datetime.now(asia_tz).strftime("%I:%M %p"),price= str(format( int(price)/3,".2f")),checkbox=get1)
        Description.objects.create(desc=desc,times=datetime.now(asia_tz).strftime("%I:%M %p"),date=date,paymentby=str(paymentby)+ f" ({price}) ")
    if Manish.objects.all().count() > 0:
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

        manish=Manish.objects.filter(date__range=(formatted_start_date, formatted_end_date)).order_by('-id')
        kazim=Kazim.objects.filter(date__range=(formatted_start_date, formatted_end_date)).order_by('-id')
        samay=Samay.objects.filter(date__range=(formatted_start_date, formatted_end_date)).order_by('-id')
        descc=Description.objects.filter(date__range=(formatted_start_date, formatted_end_date)).order_by('-id')

        total_manish = format(Manish.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")
        total_kazim = format(Kazim.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")
        total_samay = format(Samay.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")

        discount_manish = format(Manish.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('discount'))['discount__sum']  or 0.0, ".2f")
        discount_kazim = format(Kazim.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('discount'))['discount__sum']  or 0.0, ".2f")
        discount_samay = format(Samay.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('discount'))['discount__sum']  or 0.0, ".2f")



        manish_total= rent + float(total_manish) - float(discount_manish)
        manish_total=format(manish_total,".2f")
        # print(total_manish)
        # print(manish_total)
        # print(discount_manish)
        # print()

        kazim_total= rent + float(total_kazim) - float(discount_kazim)
        kazim_total=format(kazim_total ,".2f")
        # print(total_kazim)
        # print(kazim_total)
        # print(discount_kazim)

        # print()
        samay_total= rent + float(total_samay) - float(discount_samay)
        samay_total=format(samay_total ,".2f")
        # samay_total= rent + 10 - 10

        # print(total_samay)
        # print(samay_total)
        # print(discount_samay)

        data={
            "obj":zip(manish,kazim,samay,descc),
            "objs":zip(manish,kazim,samay,descc),
            "date":datetime.now(asia_tz).date(),

            "total_manish":total_manish,
            "total_kazim":total_kazim,
            "total_samay":total_samay,

            "discount_manish":discount_manish,
            "discount_kazim":discount_kazim,
            "discount_samay":discount_samay,

            "manish_total": manish_total,
            "kazim_total": kazim_total,
            "samay_total": samay_total,
            "total":format(float(manish_total)+float(kazim_total)+float(samay_total),".2f")
        }

        return render(request,"index.html",data)
    else:
        data={
            "date":datetime.now(asia_tz).date(),

        }
        return render(request,"index.html",data)




# this code is only for manish
def manish(request):
    today = datetime.now(asia_tz)

    # Determine the current month and year
    current_month = today.month
    current_year = today.year
    # Calculate the start and end dates
    if today.day >= 1:  # If today is the 1th or later, filter 1th of this month to 1th of next month
        start_date = datetime(current_year, current_month, 1,tzinfo=asia_tz)
        if current_month == 12:  # Handle year-end transition
            end_date = datetime(current_year + 1, 1, 1,tzinfo=asia_tz)
        else:
            end_date = datetime(current_year, current_month + 1, 1,tzinfo=asia_tz)
    else:  # If today is before the 1th, filter 1th of last month to 1th of this month
        if current_month == 1:  # Handle year-start transition
            start_date = datetime(current_year - 1, 12, 1,tzinfo=asia_tz)
        else:
            start_date = datetime(current_year, current_month - 1, 1,tzinfo=asia_tz)
        end_date = datetime(current_year, current_month, 1,tzinfo=asia_tz)

    # Filter data based on the calculated date range


    # Format dates as MM/DD/YY for debugging or display
    formatted_start_date = start_date.strftime('%Y-%m-%d')
    formatted_end_date = end_date.strftime('%Y-%m-%d')
    if request.method=="POST":
        price=request.POST.get("price")
        desc=request.POST.get("desc")
        date=datetime.now(asia_tz).date()
        Manish_Khata.objects.create(price=price,times=datetime.now(asia_tz).strftime("%I:%M %p"),desc=desc,date=date)
    # Get the data of whole month
    if Manish_Khata.objects.all().count() >0:
        avgs =Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date)).values("desc").annotate(desc_count=Count('desc'))
        desc_prices = []

        for i in avgs:
            m = Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date),desc=i["desc"])
            total_price = sum(j.price for j in m)  # Calculate total price
            desc_prices.append({"desc": i["desc"], "total_price": total_price})
            # Sort desc_prices by total_price in descending order
            desc_prices = sorted(desc_prices, key=lambda x: x["total_price"], reverse=True)
        # Get the data of whole Day
        avgss =Manish_Khata.objects.filter(date__range=(f'{datetime.now(asia_tz).date()}', f'{datetime.now(asia_tz).date()}')).values("desc").annotate(desc_count=Count('desc'))
        desc_pricess = []

        for i in avgss:
            m = Manish_Khata.objects.filter(date=f'{datetime.now(asia_tz).date()}',desc=i["desc"])
            total_price = sum(j.price for j in m)  # Calculate total price
            desc_pricess.append({"desc": i["desc"], "total_price": total_price})
            # Sort desc_prices by total_price in descending order
            desc_pricess = sorted(desc_pricess, key=lambda x: x["total_price"], reverse=True)
        # print(avgss)
        manish=Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date)).order_by("-id")
        total_month = format(Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")
        total_day = format(Manish_Khata.objects.filter(date__range=(datetime.now(asia_tz).date(), datetime.now(asia_tz).date())).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")
        # print("thisisis",total_day,total_month,formatted_start_date,formatted_end_date)

        data={
            "date":datetime.now(asia_tz).date(),
            "manish":manish,
            "total_month":total_month,
            "total_day":total_day,
            "avgs":desc_prices,
            "avgss":desc_pricess
        }
        return render(request,"manish.html",data)
    else:
        # manish="hi"
        data={
            "date":datetime.now(asia_tz).date(),
            # "manish":manish
        }
        return render(request,"manish.html",data)


def manish_export(request):

    if request.method=="POST":

        sdate=request.POST.get('from')
        edate=request.POST.get('to')
        # print(sdate)
        try:
            formatted_start_date = datetime.strptime(f"{sdate}", '%Y-%m-%d')
            formatted_end_date = datetime.strptime(f"{edate}", '%Y-%m-%d')
        except ValueError:
            return HttpResponse("Invalid date format. Use MM/DD/YY.", status=400)
    # Get the data of whole month
    avgs =Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date)).values("desc").annotate(desc_count=Count('desc'))
    desc_prices = []

    for i in avgs:
        m = Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date),desc=i["desc"])
        total_price = sum(j.price for j in m)  # Calculate total price
        desc_prices.append({"desc": i["desc"], "total_price": total_price})
        # Sort desc_prices by total_price in descending order
        desc_prices = sorted(desc_prices, key=lambda x: x["total_price"], reverse=True)
    # Get the data of whole Day
    desc_pricess = []
    # print(len(desc_pricess))

    # print(avgss)
    if Manish_Khata.objects.all().count() >0:
        manish=Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date)).order_by("-id")
        total = format(Manish_Khata.objects.filter(date__range=(formatted_start_date, formatted_end_date)).aggregate(Sum('price'))['price__sum'] or 0.0, ".2f")
        data={
            "date":datetime.now(asia_tz).date(),
            "manish":manish,
            "total_month":total,
            "avgs":desc_prices,
            "avgss":len(desc_pricess)
        }
        return render(request,"manish.html",data)
    else:
        # manish="hi"
        data={
            "date":datetime.now(asia_tz).date(),
            # "manish":manish
        }
        return render(request,"manish.html",data)