import math
from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def display(request):
    return HttpResponse("Hello, this is the menu page.")


def suma(request):
    result = None
    a = b = None
    if request.method == "POST":
        try:
            a = int(request.POST.get("a", 0))
            b = int(request.POST.get("b", 0))
            result = a + b
        except ValueError:
            result = "Por favor, ingrese números válidos."
    return render(request, "menu/suma.html", {"result": result, "a": a, "b": b})