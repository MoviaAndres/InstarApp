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


class BusquedaPerfilesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user('ana_luna', first_name='Ana', last_name='Rios')
        cls.bruno = User.objects.create_user('bruno_sol', first_name='Bruno', last_name='Lopez')
        cls.sara = User.objects.create_user('sara_rios', first_name='Sara', last_name='Rios')
        cls.inactivo = User.objects.create_user('ana_inactiva', is_active=False)
        for user in (cls.ana, cls.bruno, cls.sara, cls.inactivo):
            Usuario.objects.create(usuario=user, descripcion='Un perfil de prueba.')

    def buscar(self, consulta='', **params):
        return self.client.get(reverse('buscar_perfiles'), {'q': consulta, **params})

    def test_busqueda_vacia_no_lista_perfiles(self):
        for consulta in ('', '   '):
            response = self.buscar(consulta)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['perfiles'].paginator.count, 0)
            self.assertContains(response, 'Empezá una búsqueda')
            self.assertNotContains(response, '@ana_luna')

    def test_busca_usuario_parcial_con_arroba_y_mayusculas(self):
        for consulta in ('LUNA', '  @ANA  '):
            response = self.buscar(consulta)
            self.assertEqual([p.usuario for p in response.context['perfiles']], [self.ana])
            self.assertContains(response, reverse('perfil', kwargs={'username': self.ana.username}))
        self.assertEqual(response.context['consulta'], '@ANA')

    def test_busca_nombre_completo_y_apellido(self):
        response = self.buscar('Ana Rios')
        self.assertEqual([p.usuario for p in response.context['perfiles']], [self.ana])
        response = self.buscar('RIOS')
        self.assertEqual([p.usuario for p in response.context['perfiles']], [self.ana, self.sara])

    def test_muestra_mensaje_sin_coincidencias(self):
        for consulta in ('nadie_con_este_nombre', '@', '%'):
            response = self.buscar(consulta)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'No encontramos perfiles')
            self.assertEqual(response.context['perfiles'].paginator.count, 0)

    def test_no_muestra_usuarios_inactivos(self):
        response = self.buscar('ana')
        self.assertNotContains(response, '@ana_inactiva')
        self.assertContains(response, '@ana_luna')

    def test_muestra_bloqueados_propios_y_oculta_quien_bloqueo_al_buscador(self):
        self.bruno.perfil.bloqueados.add(self.ana)
        self.sara.perfil.bloqueados.add(self.bruno)
        self.client.force_login(self.bruno)
        response = self.buscar('a')
        self.assertEqual(response.context['perfiles'].paginator.count, 1)
        self.assertContains(response, '@ana_luna')
        self.assertContains(response, 'Bloqueado por vos')
        self.assertNotContains(response, '@sara_rios')
        self.assertTrue(self.bruno.perfil.bloqueados.filter(pk=self.ana.pk).exists())

    def test_bloqueo_mutuo_no_muestra_el_perfil(self):
        self.bruno.perfil.bloqueados.add(self.ana)
        self.ana.perfil.bloqueados.add(self.bruno)
        self.client.force_login(self.bruno)
        response = self.buscar('ana')
        self.assertEqual(response.context['perfiles'].paginator.count, 0)

    def test_estado_de_bloqueo_solo_se_muestra_a_su_dueno(self):
        self.bruno.perfil.bloqueados.add(self.ana)
        for user in (None, self.sara):
            if user is not None:
                self.client.force_login(user)
            response = self.buscar('ana')
            self.assertContains(response, '@ana_luna')
            self.assertNotContains(response, 'Bloqueado por vos')

    def test_bloquear_y_desbloquear_con_ids_de_cuenta_y_perfil_distintos(self):
        User.objects.create_user('cuenta_sin_perfil')
        target = User.objects.create_user('objetivo')
        profile = Usuario.objects.create(usuario=target)
        self.assertNotEqual(target.pk, profile.pk)
        self.client.force_login(self.bruno)
        url = reverse('bloquear_perfil', kwargs={'pk': profile.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.bruno.perfil.bloqueados.filter(pk=target.pk).exists())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.bruno.perfil.bloqueados.filter(pk=target.pk).exists())

    def test_usuario_sin_perfil_puede_buscar(self):
        lector = User.objects.create_user('lector')
        self.client.force_login(lector)
        response = self.buscar('luna')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '@ana_luna')

    def test_paginacion_conserva_consulta_y_no_repite_perfiles(self):
        for i in range(13):
            user = User.objects.create_user(f'grupo_{i:02d}')
            Usuario.objects.create(usuario=user)
        primera = self.buscar(' @grupo_ ')
        segunda = self.buscar('@grupo_', page=2)
        self.assertEqual(primera.context['perfiles'].paginator.count, 13)
        self.assertEqual(len(primera.context['perfiles']), 12)
        self.assertEqual(len(segunda.context['perfiles']), 1)
        self.assertContains(primera, '?q=%40grupo_&amp;page=2')
        self.assertFalse({p.pk for p in primera.context['perfiles']} & {p.pk for p in segunda.context['perfiles']})

    def test_pagina_invalida_no_genera_error(self):
        for numero in ('no-numero', '999', '-1'):
            self.assertEqual(self.buscar('ana', page=numero).status_code, 200)

    def test_consulta_se_escapa_en_html(self):
        response = self.buscar('\"><script>alert(1)</script>')
        self.assertNotContains(response, '<script>')
        self.assertContains(response, '&lt;script&gt;')

    def test_acceso_en_barra_y_formulario_solo_en_busqueda(self):
        inicio = self.client.get(reverse('home'))
        self.assertContains(inicio, 'class="enlace-busqueda" href="' + reverse('buscar_perfiles') + '"')
        self.assertNotContains(inicio, 'role="search"')
        self.assertNotContains(inicio, 'busqueda-panel')
        busqueda = self.client.get(reverse('buscar_perfiles'))
        self.assertContains(busqueda, 'role="search"')
        self.assertContains(busqueda, 'action="' + reverse('buscar_perfiles') + '"')
        perfil = self.client.get(reverse('perfil', kwargs={'username': self.ana.username}))
        self.assertContains(perfil, reverse('buscar_perfiles'))
