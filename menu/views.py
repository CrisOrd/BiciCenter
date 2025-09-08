
from django.shortcuts import render
from django.http import HttpResponse


from django.shortcuts import render

def mainPage(request):
    return render(request, 'master.html')

<<<<<<< Updated upstream
=======
def loginPage(request):
    return render(request, 'login.html')

def mantemientoPage(request):
<<<<<<< Updated upstream
    return render(request, 'mantenimiento.html')
>>>>>>> Stashed changes
=======
    return render(request, 'mantenimiento.html')
>>>>>>> Stashed changes
