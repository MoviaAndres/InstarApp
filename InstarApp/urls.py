from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio_ss', views.ingreso, name="login"),
    path('crear_ss', views.crear_cuenta, name="crear_cuenta"),
    path('', views.home, name="home"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/<str:username>/", views.perfil, name="perfil"),
    path("post/crear/", views.crear_post, name="crear_post"),
    path("post/eliminar/<int:pk>", views.eliminar_post, name="eliminar_post"),
    path("post/like/<int:pk>", views.like_post, name="like_post"),
    path("comentarios/<int:pk>", views.comentarios, name="comentarios"),
    path("comentar/<int:pk>", views.crear_comentario, name="crear_comentario")
]
