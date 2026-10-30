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

    publicaciones = Post.objects.filter(usuario=perfil_usuario.id)

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


@login_required(login_url='login')
def eliminar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    usuario = get_object_or_404(Usuario, pk=post.usuario.id)
    
    if usuario.id != request.user.id:
        return redirect("perfil", username=usuario)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post eliminado")
        return redirect("perfil", username=usuario)

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    usuario = get_object_or_404(Usuario, pk=post.usuario.id)

    if (request.method == "POST") and (usuario.id != request.user.id):

        if post.like.filter(pk=request.user.pk):
            post.like.remove(usuario)
        else:
            post.like.add(usuario)

    return redirect("perfil", username=usuario)



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

    usuario = request.user

    contexto = {
        "usuario": usuario,
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