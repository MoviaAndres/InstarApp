from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.utils import timezone
from .models import Usuario
from .forms import UsuarioForm
# Create your views here.


def crear_cuenta(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = UsuarioForm()

    return render(
        request,
        "usuarioform.html",
        {"form": form}
    )


def ingreso(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("home")

        return render(
            request,
            "login",
            {"error": "Usuario o contraseña incorrectos."}
        )

    return render(request, "login.html")


def home(request):
    
    return render(request, 'home.html')