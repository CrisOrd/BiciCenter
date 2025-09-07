
from django.shortcuts import render
from django.http import HttpResponse


from django.shortcuts import render

def mainPage(request):
    return render(request, 'master.html')

def loginPage(request):
    return render(request, 'login.html')