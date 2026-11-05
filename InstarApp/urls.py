from django.urls import path
from . import views

urlpatterns = [
    path('moderador', views.moderador, name="moderador"),
    path('salir/', views.salir, name='logout'),
    path('inicio_ss', views.ingreso, name="login"),
    path('crear_ss', views.crear_cuenta, name="crear_cuenta"),
    path('', views.home, name="home"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/<str:username>/", views.perfil, name="perfil"),
    path("perfil/eliminar/<int:pk>",views.eliminar_usuario, name ="eliminar_usuario"),
    path("perfil/advertir/<int:pk>", views.advertir_usuario, name="advertir_usuario"),
    path("perfil/permitir/<int:pk>", views.permitir_usuario, name="permitir_usuario"),
    path("post/crear/", views.crear_post, name="crear_post"),
    path("post/eliminar/<int:pk>", views.eliminar_post, name="eliminar_post"),
    path("post/advertir/<int:pk>", views.advertir_post, name="advertir_post"),
    path("post/permitir/<int:pk>", views.permitir_post, name="permitir_post"),
    path("post/like/<int:pk>", views.like_post, name="like_post"),
    path("comentarios/<int:pk>", views.comentarios, name="comentarios"),
    path("comentar/<int:pk>", views.crear_comentario, name="crear_comentario"),
    path("comentarios/like/<int:pk>", views.like_comentario, name="like_comentario"),
    path("comentarios/eliminar/<int:pk>", views.eliminar_comentario, name="eliminar_comentario"),
    path("comentarios/advertir/<int:pk>", views.advertir_comentario, name="advertir_comentario"),
    path("comentarios/permitir/<int:pk>", views.permitir_comentario, name="permitir_comentario"),
]
