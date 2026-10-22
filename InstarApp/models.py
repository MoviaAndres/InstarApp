from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.


class Usuario (models.Model):

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    foto_perfil= models.ImageField(blank=True, null=True)
    descripcion= models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.usuario.username

class Post (models.Model):

    usuario= models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="post_usuario")
    imagen= models.ImageField(blank=True, null=True)
    texto= models.CharField(max_length=1000, blank=True)
    like= models.ManyToManyField(Usuario, related_name="post_like")

class Comentario (models.Model):

    usuario= models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="comentario_usuario")
    post= models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comentario_like")
    texto= models.CharField(max_length=500)
    like= models.ManyToManyField(Usuario)
    
