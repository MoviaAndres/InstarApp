from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio_ss', views.ingreso, name="login"),
    path('crear_ss', views.crear_cuenta, name="crear_cuenta"),
    path('', views.home, name="home")
]
