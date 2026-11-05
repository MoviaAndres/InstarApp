from django.contrib import admin
from .models import Post, Usuario, Comentario
# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('usuario','texto')
    search_fields = ('usuario','texto')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario','moderador')
    search_fields = ('usuario',)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario',)
    search_fields = ('usuario','texto')