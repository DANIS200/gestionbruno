from django.http import response
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .models import Profile
import pdfkit
from django.template.loader import get_template
import io
from weasyprint import html

# Create your views here.
def index(request):
    return render(request, 'archive/index.html')

def formulaire(request):
    if request.method == "POST":
        name = request.POST.get("name")          
        phone = request.POST.get("phone")    
        address = request.POST.get("address")    
        activite = request.POST.get("activite")  
        contrat = request.POST.get("contrat")  
        articles = request.POST.get("articles")    
        materiels = request.POST.get("materiels")    
        donnees = Profile(name=name,  phone=phone, address=address, activite=activite,  contrat=contrat, articles=articles, materiels= materiels) 
        donnees.save()
        return redirect('verification')
    return render(request, 'archive/formulaire.html')

def verification(request):
    profiles = Profile.objects.all()[:1]
    for profile in profiles:
        name=profile.name
        phone=profile.phone
        address =profile.address
        activite = profile.activite
        contrat = profile.contrat
        articles = profile.articles
        materiels = profile.materiels 
    return render(request, "archive/verification.html", {'address':address, 'name':name, 'phone':phone, 'activite':activite, 'contrat':contrat, 'articles':articles, 'materiels': materiels })

def generer(request, id):
    profile = Profile.objects.get(pk=id)
    name=profile.name
    phone=profile.phone
    address =profile.address
    activite = profile.activite
    contrat = profile.contrat
    articles = profile.articles
    materiels = profile.materiels

    template = get_template('archive/generator.html')
    context = {'address':address, 'name':name,'phone':phone, 'activite':activite, 'contrat':contrat, 'articles':articles, 'materiels': materiels }
    html = template.render(context)
    options = {
        'page-size':'Letter',
        'encoding':'UTF-8',
    }
    pdf = pdfkit.from_string(html, False, options)

    reponse = HttpResponse(pdf, content_type='application/pdf')
    reponse['Content-Disposition']="attachement"
    return reponse

def download(request):
    profile = Profile.objects.all()
    return render(request, 'archive/download.html', {'profile':profile}) 

