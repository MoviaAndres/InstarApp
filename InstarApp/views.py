from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.utils import timezone
from .models import Usuario, Post, Comentario
from .forms import UsuarioForm, PerfilForm, PostForm, ComentarioForm
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

@login_required
def moderador(request):
    usuario = request.user.perfil
    if not usuario.moderador:
        return render(request, 'home.html')
    
    publicaciones = Post.objects.filter(advertencia=True)
    comentarios = Comentario.objects.filter(advertencia=True)
    usuarios = Usuario.objects.filter(advertencia=True)
    contexto = {
        "publicaciones": publicaciones,
        "comentarios": comentarios,
        "usuarios": usuarios
    }

    return render(request, "moderador.html", contexto)

def perfil(request, username):
    if request.user.is_authenticated:
        usuario_actual = getattr(request.user, "perfil", None)
    else:
        usuario_actual = None
        
    perfil_usuario = get_object_or_404(
        Usuario.objects.select_related("usuario"),
        usuario__username=username
    )

    publicaciones = Post.objects.filter(usuario=perfil_usuario.id)

    es_dueno = (
        request.user.is_authenticated
        and request.user.pk == perfil_usuario.usuario_id
    )

    form_post = PostForm() if es_dueno else None

    contexto = {
        "usuario": usuario_actual,
        "perfil": perfil_usuario,
        "publicaciones": publicaciones,
        "es_dueno": es_dueno,
        "form_post": form_post,
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


@login_required(login_url='login')
def eliminar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    usuario_post = get_object_or_404(Usuario, pk=post.usuario.id)
    usuario = request.user.perfil
    if (usuario_post.id != request.user.id) and not usuario.moderador:
        return redirect("perfil", username=usuario_post)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post eliminado")
        return redirect("perfil", username=usuario_post)

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    usuario_post = get_object_or_404(Usuario, pk=post.usuario.id)
    usuario = request.user.perfil

    if (request.method == "POST") and (usuario_post.id != request.user.id):

        if post.like.filter(usuario_id=request.user.id):
            post.like.remove(usuario)
        else:
            post.like.add(usuario)

    return redirect("perfil", username=usuario_post)


@login_required(login_url='login')
def advertir_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.advertir()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def permitir_post(request, pk):
    
    usuario = request.user.perfil
    if not usuario.moderador:
        return redirect("home")
    
    post = get_object_or_404(Post, pk=pk)
    post.permitir()

    return redirect("moderador")


@login_required
def like_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    usuario_post = get_object_or_404(Usuario, pk=comentario.usuario.id)
    usuario = request.user.perfil
    post = get_object_or_404(Post,pk=comentario.post.id)


    if comentario.like.filter(usuario_id=request.user.id):
        comentario.like.remove(usuario)
    else:
        comentario.like.add(usuario)

    return redirect("comentarios", post.id)


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

def comentarios(request,pk):
    post = get_object_or_404(Post, pk=pk)
    comentarios = Comentario.objects.filter(post=post.id)

    if request.user.is_authenticated:
        usuario_actual = getattr(request.user, "perfil", None)
    else:
        usuario_actual = None

    contexto = {
        "usuario": usuario_actual,
        "post": post,
        "comentarios": comentarios,
        "form_post": ComentarioForm(),
    }

    return render(request, "comentarios.html", contexto)


@login_required
def crear_comentario(request,pk):
    if request.method == "POST":
        form = ComentarioForm(request.POST, request.FILES)

        if form.is_valid():
            comentario = form.save(commit=False)

            # El autor siempre es el usuario autenticado
            comentario.usuario = get_object_or_404(
                Usuario,
                usuario=request.user
            )

            comentario.post = get_object_or_404(Post,pk=pk)

            comentario.save()

            messages.success(request, "Comentario Publicado.")

    return redirect(
        "comentarios",
        pk
    )

@login_required(login_url='login')
def eliminar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    usuario = request.user.perfil
    if not usuario.moderador:
        return redirect(
        "home",
        pk
        )
    
    if request.method == 'POST':
        comentario.delete()
        messages.success(request, "Comentario eliminado")
        return redirect(
            "moderador"
        )


@login_required(login_url='login')
def advertir_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.advertir()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def permitir_comentario(request, pk):
    
    usuario = request.user.perfil
    if not usuario.moderador:
        return redirect("home")
    
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.permitir()

    return redirect("moderador")

@login_required(login_url='login')
def eliminar_usuario(request, pk):
    usuario_eliminar = get_object_or_404(Usuario, pk=pk)
    usuario = request.user.perfil
    if not usuario.moderador:
        return redirect(
        "home"
        )
    
    if request.method == 'POST':
        usuario_eliminar.delete()
        messages.success(request, "Post eliminado")
        return redirect(
            "moderador"
        )


@login_required(login_url='login')
def advertir_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.advertir()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def permitir_usuario(request, pk):
    
    usuario = request.user.perfil
    if not usuario.moderador:
        return redirect("home")
    
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.permitir()

    return redirect("moderador")