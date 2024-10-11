from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
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

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, save_by=request.user) | Expense.objects.filter(
            date__istartswith=search_str, save_by=request.user) | Expense.objects.filter(
            description__icontains=search_str, save_by=request.user) | Expense.objects.filter(
            category__icontains=search_str, save_by=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(save_by=request.user)
    paginator = Paginator(expenses,4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'expenses': expenses,
        'page_obj':page_obj,
    }
    return render(request, 'expenses/index.html', context)

 

def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(save_by=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')


def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.save_by = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')
    
    
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content_Disposition']='attachment; filename=Expenses'+\
        str(datetime.datetime.now())+'.csv'
    
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])
    
    expenses=Expense.objects.filter(save_by=request.user)

    for expense in expenses :
        writer.writerow([expense.amount,expense.description,
                         expense.category,expense.date])
    return response



def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content_Disposition']='attachment; filename=Expenses'+\
        str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style= xlwt.XFStyle()
    font_style.font.bold=True

    columns= ['Amount','Description','Category','Date']
    
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)
        font_style = xlwt.XFStyle()

    rows =Expense.objects.filter(save_by=request.user).values_list(
        'amount','description','category','date')
    for row in rows:
       row_num +=1
       for col_num in range(len(row)):
           ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    
    return response
  

def export_pdf(request):
    response=HttpResponse(content_type='application/pdf')
    response['Content_Disposition']='inline; attachment; filename=Expenses'+\
       str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses=Expense.objects.filter(save_by=request.user)

    sum = expenses.aggregate(Sum('amount'))

    html_string = render_to_string(
        'expenses/pdf-output.html',{'expenses':expenses,'total':sum})
    html=HTML(string=html_string)
   
    result = html.write_pdf()


    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())  

    return response
   
from django.db.models import Sum

@login_required
def summary_by_category(request):
    # Calculer la somme des dépenses par catégorie pour l'utilisateur connecté
    expenses_by_category = Expense.objects.filter(save_by=request.user) \
        .values('category') \
        .annotate(total_amount=Sum('amount'))

    # Préparer les données pour le graphique
    categories = [expense['category'] for expense in expenses_by_category]
    amounts = [expense['total_amount'] for expense in expenses_by_category]

    # Calculer la somme totale de toutes les dépenses
    total_expenses = Expense.objects.filter(save_by=request.user) \
        .aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses_by_category': expenses_by_category,
        'total_expenses': total_expenses,
        'categories': json.dumps(categories),  # Catégories au format JSON
        'amounts': json.dumps(amounts),        # Montants au format JSON
    }

    return render(request, 'expenses/summary_by_category.html', context)


