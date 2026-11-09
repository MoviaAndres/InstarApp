import copy
import json
from pathlib import Path
import sqlite3

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.contrib.auth.models import User, Group
from InstarApp.models import Usuario, Post, Comentario


class Command(BaseCommand):
    help = 'Exporta una copia local consistente para trasladar las cuentas y publicaciones.'

    def add_arguments(self, parser):
        parser.add_argument('--output', required=True, help='Carpeta privada de destino, excluida de Git.')

    def handle(self, *args, **options):
        config = connections['default'].settings_dict
        if config['ENGINE'] != 'django.db.backends.sqlite3' or str(config['NAME']) == ':memory:':
            raise CommandError('Ejecutá la exportación con settings.py y tu base SQLite local.')
        output = Path(options['output']).resolve()
        output.mkdir(parents=True, exist_ok=True)
        names = ['database.sqlite3', 'datos.json', 'media-manifest.json', 'counts.json']
        if any((output / name).exists() for name in names):
            raise CommandError('El destino ya contiene una exportación; elegí otra carpeta.')

        source = Path(config['NAME']).resolve()
        with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as original:
            with sqlite3.connect(output / 'database.sqlite3') as backup:
                original.backup(backup)

        alias = 'deployment_export'
        backup_config = copy.deepcopy(config)
        backup_config.update(NAME=str(output / 'database.sqlite3'), OPTIONS={})
        connections.databases[alias] = backup_config
        try:
            with transaction.atomic(using=alias):
                # Windows puede usar otra codificación por defecto; el destino es UTF-8.
                with (output / 'datos.json').open('w', encoding='utf-8') as stream:
                    call_command('dumpdata', 'auth.User', 'auth.Group', 'InstarApp',
                                 '--natural-foreign', '--indent', '2', database=alias,
                                 stdout=stream, verbosity=0)
                models = {'usuarios': User, 'grupos': Group, 'perfiles': Usuario,
                          'publicaciones': Post, 'comentarios': Comentario,
                          'seguidores': Usuario.seguidores.through,
                          'bloqueados': Usuario.bloqueados.through,
                          'likes_publicaciones': Post.like.through,
                          'likes_comentarios': Comentario.like.through}
                counts = {key: model.objects.using(alias).count() for key, model in models.items()}
                files = set(Usuario.objects.using(alias).exclude(foto_perfil='')
                            .values_list('foto_perfil', flat=True))
                files.update(Post.objects.using(alias).exclude(imagen='').values_list('imagen', flat=True))
        finally:
            connections[alias].close()

        media_root = Path(settings.MEDIA_ROOT).resolve()
        manifest = []
        for name in sorted(value for value in files if value):
            path = (media_root / name).resolve()
            if not path.is_relative_to(media_root):
                raise CommandError('Una imagen referencia un archivo fuera de la carpeta media.')
            manifest.append({'name': name, 'exists': path.is_file()})
        (output / 'counts.json').write_text(json.dumps(counts, indent=2), encoding='utf-8')
        (output / 'media-manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
        missing = sum(not item['exists'] for item in manifest)
        self.stdout.write(self.style.SUCCESS(f'Exportación local terminada. Imágenes referenciadas: {len(manifest)}; faltantes: {missing}.'))
