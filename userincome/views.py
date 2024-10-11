from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json

from django.http import JsonResponse,HttpResponse
import datetime
import csv
import xlwt

from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, save_by=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, save_by=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, save_by=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, save_by=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(save_by=request.user)
    paginator = Paginator(income, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    user = request.user
    context = {
        'income': income,
        'page_obj': page_obj,
    }
    return render(request, 'income/index.html', context)


def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(save_by=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('income')

def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')


def userIncome_source_summary(request):
    todays_date =datetime.date.today()
    six_months_ago =todays_date-datetime.timedelta(days=30*6)
    userIncomes = UserIncome.objects.filter(save_by=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date
    )
    finalrep={}

    def get_source(userIncome):
        return userIncome.category
    source_list = list(set(map(get_source,userIncomes)))

    def get_userIncome_source_amount(source):
        amount = 0
        filter_by_source=userIncomes.filter(source=source)

        for item in filter_by_source:
            amount += item.amount
        return amount

    for x in userIncomes:
        for y in source_list:
            finalrep[y]=get_userIncome_source_amount(y)

    return JsonResponse({'expense_category_data':finalrep},safe=False)


def stats_view(request):
    return render(request,'income/stat.html')



def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content_Disposition']='attachment; filename=UserIncomes'+\
        str(datetime.datetime.now())+'.csv'
    
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])
    
    userIncomes=UserIncome.objects.filter(save_by=request.user)

    for userIncome in userIncomes :
        writer.writerow([userIncome.amount,userIncome.description,
                         userIncome.source,userIncome.date])
    return response



def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content_Disposition']='attachment; filename=UserIncomes'+\
        str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('UserIncomes')
    row_num=0
    font_style= xlwt.XFStyle()
    font_style.font.bold=True

    columns= ['Amount','Description','Source','Date']
    
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)
        font_style = xlwt.XFStyle()

    rows =UserIncome.objects.filter(save_by=request.user).values_list(
        'amount','description','source','date')
    for row in rows:
       row_num +=1
       for col_num in range(len(row)):
           ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    
    return response
  

def export_pdf(request):
    response=HttpResponse(content_type='application/pdf')
    response['Content_Disposition']='inline; attachment; filename=UserIncomes'+\
       str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    userIncomes=UserIncome.objects.filter(save_by=request.user)

    sum = userIncomes.aggregate(Sum('amount'))

    html_string = render_to_string(
        'income/pdf-output.html',{'userIncomes':userIncomes,'total':sum})
    html=HTML(string=html_string)
   
    result = html.write_pdf()


    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())  

    return response


@login_required
def summary_by_source(request):
    # Récupérer la somme des revenus par source pour l'utilisateur connecté
    income_by_source = UserIncome.objects.filter(save_by=request.user) \
        .values('source') \
        .annotate(total_amount=Sum('amount'))

    # Calculer la somme totale des revenus
    total_income = UserIncome.objects.filter(save_by=request.user) \
        .aggregate(total=Sum('amount'))['total'] or 0

    # Préparer les données pour le graphique
    sources = [income['source'] for income in income_by_source]
    amounts = [income['total_amount'] for income in income_by_source]

    context = {
        'income_by_source': income_by_source,
        'total_income': total_income,
        'sources': json.dumps(sources),  # Convertir en JSON pour Chart.js
        'amounts': json.dumps(amounts),  # Convertir en JSON pour Chart.js
    }

    return render(request, 'income/summary_by_source.html', context)

   

