from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Usuario



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