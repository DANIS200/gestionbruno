from os import name
from . import views
from django.urls import path
from archive.views import index, formulaire, verification,generer, download

urlpatterns = [
    path('', index, name="archive"),
    path('formulaire',formulaire, name="formulaire"),
    path('verification', verification, name="verification"),
    path('<int:id>', generer, name="generer"),
    path('download', download, name="download")
]