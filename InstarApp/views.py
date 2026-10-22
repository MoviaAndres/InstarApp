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
from .forms import UsuarioForm, PerfilForm, PostForm
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

def perfil(request, username):
    perfil_usuario = get_object_or_404(
        Usuario.objects.select_related("usuario"),
        usuario__username=username
    )

    publicaciones = perfil_usuario.post_usuario.all().order_by("-id")

    es_dueno = (
        request.user.is_authenticated
        and request.user.pk == perfil_usuario.usuario_id
    )

    contexto = {
        "perfil": perfil_usuario,
        "publicaciones": publicaciones,
        "es_dueno": es_dueno,
        "form_post": PostForm() if es_dueno else None,
    }

    return render(request, "perfil.html", contexto)


@login_required
def editar_perfil(request):
    perfil_usuario = get_object_or_404(
        Usuario,
        usuario=request.user
    )

    if request.method == "POST":
        form = PerfilForm(
            request.POST,
            request.FILES,
            instance=perfil_usuario
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect(
                "perfil",
                username=request.user.username
            )
    else:
        form = PerfilForm(instance=perfil_usuario)

    return render(
        request,
        "editar_perfil.html",
        {"form": form}
    )


@login_required
def crear_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)

            # El autor siempre es el usuario autenticado
            post.usuario = get_object_or_404(
                Usuario,
                usuario=request.user
            )

            post.save()

            messages.success(request, "Publicación creada.")

    return redirect(
        "perfil",
        username=request.user.username
    )