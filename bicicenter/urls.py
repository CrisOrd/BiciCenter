from django.contrib import admin
from django.urls import path
from  menu import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', views.mainPage, name='menu'),
    path('login/', views.loginPage, name='login'),
    path('registrar/', views.registrarPage, name='registrar'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),
]