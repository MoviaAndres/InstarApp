import json
from pathlib import Path

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Comprueba las fotos exportadas y, con --upload, las copia al bucket privado.'

    def add_arguments(self, parser):
        parser.add_argument('--manifest', required=True)
        parser.add_argument('--source', required=True, help='Carpeta media local original.')
        parser.add_argument('--upload', action='store_true')
        parser.add_argument('--allow-missing', action='store_true')

    def handle(self, *args, **options):
        root = Path(options['source']).resolve()
        manifest = json.loads(Path(options['manifest']).read_text(encoding='utf-8'))
        available, missing = [], []
        for item in manifest:
            name = item['name']
            relative = Path(name)
            path = (root / relative).resolve()
            if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root):
                raise CommandError('El manifiesto incluye una ruta fuera de media.')
            if path.is_file():
                available.append((name, path))
            else:
                missing.append(name)
        self.stdout.write(f'Archivos disponibles: {len(available)}; faltantes: {len(missing)}.')
        if not options['upload']:
            self.stdout.write('Comprobación terminada; no se transfirió ningún archivo.')
            return
        if missing and not options['allow_missing']:
            raise CommandError('Hay imágenes faltantes. Restauralas o usá --allow-missing si aceptás omitirlas.')
        uploaded, skipped = 0, 0
        for name, path in available:
            if default_storage.exists(name):
                skipped += 1
                continue
            with path.open('rb') as stream:
                saved_name = default_storage.save(name, File(stream, name=path.name))
            if saved_name != name:
                raise CommandError('El almacenamiento cambió un nombre; revisá el archivo antes de continuar.')
            uploaded += 1
        self.stdout.write(self.style.SUCCESS(f'Fotos copiadas: {uploaded}; ya existentes: {skipped}; omitidas: {len(missing)}.'))
