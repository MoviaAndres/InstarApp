from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Usuario, Post, Comentario

from .constants import banPalabra, riesgoPalabra

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
    def clean_descripcion(self):
        texto = self.cleaned_data.get("descripcion", "")

        if not texto == None:
            texto_minusculas = texto.lower()
        else:
            texto_minusculas = ""

        if banPalabra(texto_minusculas):
            raise ValidationError(
                f"Tu publicación contiene una palabra no permitida"
            )
        
        return texto



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
    def clean_texto(self):
        texto = self.cleaned_data.get("texto", "")

        if not texto == None:
            texto_minusculas = texto.lower()
        else:
            texto_minusculas = ""

        if banPalabra(texto_minusculas):
            raise ValidationError(
                f"Tu publicación contiene una palabra no permitida"
            )
        if riesgoPalabra(texto_minusculas):
            self.advertencia = True
        return texto

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["texto"]

        widgets = {
            "texto": forms.Textarea(attrs={
                "placeholder": "Comenta",
                "rows": 3,
                "maxlength": 150,
            }),
        }
    def clean_texto(self):
        texto = self.cleaned_data.get("texto") or ""
        if not texto == None:
            texto_minusculas = texto.lower()
        else:
            texto_minusculas = ""

        if banPalabra(texto_minusculas):
            raise ValidationError(
                f"Tu publicación contiene una palabra no permitida"
            )
        
        if riesgoPalabra(texto_minusculas):
            self.advertencia = True
        return texto
    def save(self, commit=True):
        comentario = super().save(commit=False)

        comentario.advertencia = getattr(self, "advertencia", False)

        if commit:
            comentario.save()
            self.save_m2m()

        return comentario