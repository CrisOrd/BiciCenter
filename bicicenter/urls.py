from django.contrib import admin
from django.urls import path
from  menu import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', views.display, name='menu'),
    path('suma/', views.suma, name='suma'),
]
