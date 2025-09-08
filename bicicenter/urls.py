from django.contrib import admin
from django.urls import path
from  menu import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', views.mainPage, name='menu'),
<<<<<<< Updated upstream
=======
    path('login/', views.loginPage, name='login'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),    
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
]