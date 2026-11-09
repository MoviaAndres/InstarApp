import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from unittest import skipUnless
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse
from InstarApp.models import Usuario, Post, Comentario
from django.core import serializers


class DeploymentTests(TestCase):
    def test_health_y_fallo_de_base(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertIn('no-store', response['Cache-Control'])
        with patch('INSTAR.deployment.connection.cursor', side_effect=DatabaseError):
            self.assertEqual(self.client.get(reverse('health')).status_code, 503)

    def test_reportar_requiere_post(self):
        user = User.objects.create_user('reportante')
        author = User.objects.create_user('autor')
        Usuario.objects.create(usuario=user)
        profile = Usuario.objects.create(usuario=author)
        post = Post.objects.create(usuario=profile, texto='Ejemplo')
        comment = Comentario.objects.create(usuario=profile, post=post, texto='Comentario')
        self.client.force_login(user)
        for name, obj in [('reportar_usuario', profile), ('reportar_post', post), ('reportar_comentario', comment)]:
            url = reverse(name, kwargs={'pk': obj.pk})
            self.assertEqual(self.client.get(url).status_code, 405)
            obj.refresh_from_db()
            self.assertFalse(obj.advertencia)
            self.assertEqual(self.client.post(url).status_code, 302)
            obj.refresh_from_db()
            self.assertTrue(obj.advertencia)

    def test_respuestas_de_cuentas_no_se_cachean(self):
        with override_settings(MIDDLEWARE=[*settings.MIDDLEWARE, 'INSTAR.deployment.PrivateResponsesMiddleware']):
            response = self.client.get(reverse('login'))
            self.assertEqual(response['Cache-Control'], 'private, no-store')

    def test_preparar_base_rechaza_sqlite(self):
        with self.assertRaises(CommandError):
            call_command('prepare_database', stdout=io.StringIO())

    def test_importacion_inicial_desde_objeto_privado(self):
        user = User.objects.create_user('migrado')
        profile = Usuario.objects.create(usuario=user)
        payload = serializers.serialize('json', [user, profile]).encode('utf-8')
        user.delete()
        with patch.dict(os.environ, {'BOOTSTRAP_FIXTURE_KEY': 'private/test.json'}):
            with patch('InstarApp.management.commands.bootstrap_data.default_storage.open', return_value=io.BytesIO(payload)):
                call_command('bootstrap_data', stdout=io.StringIO())
            self.assertTrue(Usuario.objects.filter(usuario__username='migrado').exists())
            with patch('InstarApp.management.commands.bootstrap_data.default_storage.open') as download:
                call_command('bootstrap_data', stdout=io.StringIO())
                download.assert_not_called()


class MediaDeployTests(SimpleTestCase):
    def test_comprobacion_no_transfiere_archivos(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'foto.png').write_bytes(b'ejemplo')
            manifest = root / 'manifest.json'
            manifest.write_text(json.dumps([{'name': 'foto.png'}]), encoding='utf-8')
            with patch('InstarApp.management.commands.upload_deploy_media.default_storage') as storage:
                call_command('upload_deploy_media', manifest=str(manifest), source=str(root), stdout=io.StringIO())
                storage.exists.assert_not_called()
                storage.save.assert_not_called()

    def test_no_lee_fuera_de_la_carpeta_de_fotos(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'media'
            source.mkdir()
            manifest = root / 'manifest.json'
            manifest.write_text(json.dumps([{'name': '../privado.txt'}]), encoding='utf-8')
            with self.assertRaises(CommandError):
                call_command('upload_deploy_media', manifest=str(manifest), source=str(source), stdout=io.StringIO())


@skipUnless(importlib.util.find_spec('dj_database_url') and importlib.util.find_spec('storages'), 'Requiere requirements-production.txt')
class ProductionConfigTests(SimpleTestCase):
    ENV = {
        'DJANGO_SECRET_KEY': 'test-only-' + '1234567890abcdef' * 4,
        'DATABASE_URL': 'postgresql://postgres.test:password@localhost:5432/postgres',
        'PUBLIC_SITE_URL': 'https://instar-test.netlify.app',
        'RENDER_EXTERNAL_HOSTNAME': 'instar-test.onrender.com',
        'SUPABASE_S3_ENDPOINT': 'https://project.storage.supabase.co/storage/v1/s3',
        'SUPABASE_S3_ACCESS_KEY_ID': 'test-key',
        'SUPABASE_S3_SECRET_ACCESS_KEY': 'test-secret',
        'SUPABASE_STORAGE_REGION': 'sa-east-1',
    }

    def production(self, **changes):
        with patch.dict(os.environ, {**self.ENV, **changes}):
            return importlib.reload(importlib.import_module('INSTAR.production'))

    def test_tablas_privadas_y_sin_sqlite_en_produccion(self):
        prod = self.production()
        self.assertFalse(prod.DEBUG)
        self.assertIn('instar-test.netlify.app', prod.ALLOWED_HOSTS)
        self.assertTrue(prod.SESSION_COOKIE_SECURE)
        self.assertEqual(prod.DATABASES['default']['OPTIONS']['options'], '-c search_path=instar')
        self.assertEqual(prod.DATABASES['default']['OPTIONS']['sslmode'], 'require')

    def test_rechaza_configuracion_incompleta_o_insegura(self):
        from django.core.exceptions import ImproperlyConfigured
        for changes in [{'DJANGO_SECRET_KEY': ''}, {'PUBLIC_SITE_URL': 'http://ejemplo.com'}, {'DATABASE_URL': 'sqlite:///db.sqlite3'}]:
            with self.assertRaises(ImproperlyConfigured):
                self.production(**changes)

    def test_fotos_usan_enlaces_firmados_temporales(self):
        from storages.backends.s3 import S3Storage
        storage = S3Storage(**self.production().STORAGES['default']['OPTIONS'])
        url = storage.url('foto.png')
        parsed = urlsplit(url)
        self.assertEqual(parsed.scheme, 'https')
        self.assertIn('/instar-media/foto.png', parsed.path)
        self.assertEqual(parse_qs(parsed.query)['X-Amz-Expires'], ['900'])
