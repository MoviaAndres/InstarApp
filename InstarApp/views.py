from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .models import Usuario
from .forms import UsuarioForm, PerfilForm, PostForm
# Create your views here.


def crear_cuenta(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta creada. Ya podés iniciar sesión.")
            return redirect("login")
    else:
        form = UsuarioForm()

    return render(
        request,
        "usuarioform.html",
        {"form": form}
    )


def ingreso(request):
    siguiente = request.POST.get("next", request.GET.get("next", ""))
    if not url_has_allowed_host_and_scheme(siguiente, {request.get_host()}, require_https=request.is_secure()):
        siguiente = ""
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
            return redirect(siguiente or "home")

        return render(
            request,
            "login.html",
            {"error": "Usuario o contraseña incorrectos.", "next": siguiente, "username": username}
        )

    return render(request, "login.html", {"next": siguiente})


@require_POST
def salir(request):
    logout(request)
    return redirect("home")


def home(request):
    
    return render(request, 'home.html')

def perfil(request, username, form_post=None):
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
        "form_post": (form_post if form_post is not None else PostForm()) if es_dueno else None,
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
        else:
            return perfil(request, request.user.username, form_post=form)

    return redirect(
        "perfil",
        username=request.user.username
    )