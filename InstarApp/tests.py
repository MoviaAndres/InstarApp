from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Usuario, Post


class RecorridosTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('andres', password='Clave-Prueba-934!')
        Usuario.objects.create(usuario=self.user)

    def test_paginas_y_css(self):
        for name in ('home', 'login', 'crear_cuenta'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '/static/css/estilos.css')
        self.assertEqual(reverse('admin:index'), '/admin/')

    def test_login_incorrecto(self):
        response = self.client.post(reverse('login'), {'username': 'andres', 'password': 'incorrecta'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos.')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_regresa_a_perfil_y_logout(self):
        destino = reverse('editar_perfil')
        self.assertRedirects(self.client.get(destino), reverse('login') + '?next=' + destino)
        response = self.client.post(reverse('login'), {'username': 'andres', 'password': 'Clave-Prueba-934!', 'next': destino})
        self.assertRedirects(response, destino)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_rechaza_redireccion_externa(self):
        response = self.client.post(reverse('login'), {'username': 'andres', 'password': 'Clave-Prueba-934!', 'next': 'https://otro.example/'})
        self.assertRedirects(response, reverse('home'))

    def test_registro_crea_perfil_y_clave_cifrada(self):
        response = self.client.post(reverse('crear_cuenta'), {'username': 'nueva', 'password1': 'Otra-Clave-823!', 'password2': 'Otra-Clave-823!'})
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='nueva')
        self.assertTrue(user.check_password('Otra-Clave-823!'))
        self.assertTrue(Usuario.objects.filter(usuario=user).exists())

    def test_registro_invalido_no_crea_usuario(self):
        response = self.client.post(reverse('crear_cuenta'), {'username': 'nueva', 'password1': 'abc', 'password2': 'def'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='nueva').exists())

    def test_perfil_edicion_y_publicacion(self):
        url = reverse('perfil', kwargs={'username': 'andres'})
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(self.user)
        self.assertRedirects(self.client.post(reverse('editar_perfil'), {'descripcion': 'Hola Instar'}), url)
        self.user.perfil.refresh_from_db()
        self.assertEqual(self.user.perfil.descripcion, 'Hola Instar')
        self.assertRedirects(self.client.post(reverse('crear_post'), {'texto': 'Mi publicación'}), url)
        self.assertEqual(Post.objects.get().usuario.usuario_id, self.user.pk)
        response = self.client.post(reverse('crear_post'), {'texto': 'x' * 1001})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_post'].errors)
        self.assertEqual(Post.objects.count(), 1)

    def test_perfil_ajeno_no_muestra_formulario(self):
        otro = User.objects.create_user('otro')
        Usuario.objects.create(usuario=otro)
        self.client.force_login(otro)
        response = self.client.get(reverse('perfil', kwargs={'username': 'andres'}))
        self.assertFalse(response.context['es_dueno'])
        self.assertIsNone(response.context['form_post'])
