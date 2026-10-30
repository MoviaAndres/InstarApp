from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Usuario, Post, Comentario



class UsuarioForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def save(self, commit=True):
        usuario = super().save(commit=False)

        if commit:
            usuario.save()
            Usuario.objects.create(
                usuario=usuario,
            )

        return usuario

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["foto_perfil", "descripcion"]

        widgets = {
            "descripcion": forms.Textarea(attrs={
                "placeholder": "Cuéntanos algo sobre ti...",
                "rows": 4,
                "maxlength": 500,
            }),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["texto", "imagen"]

        widgets = {
            "texto": forms.Textarea(attrs={
                "placeholder": "¿Qué estás pensando?",
                "rows": 3,
                "maxlength": 1000,
            }),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["texto"]

        widgets = {
            "texto": forms.Textarea(attrs={
                "placeholder": "Comenta",
                "rows": 3,
                "maxlength": 500,
            }),
        }