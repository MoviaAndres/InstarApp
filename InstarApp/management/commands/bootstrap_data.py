import json
import os
from pathlib import Path
import tempfile

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Importa la primera copia desde un objeto privado, solo si todavía no hay cuentas.'

    def handle(self, *args, **options):
        key = os.environ.get('BOOTSTRAP_FIXTURE_KEY', '').strip()
        if not key:
            self.stdout.write('No hay una importación inicial configurada.')
            return
        if User.objects.exists():
            self.stdout.write('Ya hay cuentas: no se modifica la información existente.')
            return
        with default_storage.open(key, 'rb') as stream:
            payload = stream.read(10 * 1024 * 1024 + 1)
        if len(payload) > 10 * 1024 * 1024:
            raise CommandError('La copia inicial supera el tamaño admitido.')
        try:
            records = json.loads(payload.decode('utf-8'))
            allowed = {'auth.user', 'auth.group', 'instarapp.usuario', 'instarapp.post', 'instarapp.comentario'}
            if not isinstance(records, list) or any(item['model'].lower() not in allowed for item in records):
                raise ValueError('Modelos no admitidos')
        except (UnicodeError, ValueError, KeyError, TypeError) as error:
            raise CommandError('La copia inicial no tiene el formato esperado.') from error
        with tempfile.TemporaryDirectory(prefix='instar-import-') as directory:
            fixture = Path(directory) / 'datos.json'
            fixture.write_bytes(payload)
            with transaction.atomic():
                call_command('loaddata', str(fixture), verbosity=0)
        self.stdout.write(self.style.SUCCESS('Copia inicial importada. El objeto de respaldo continúa privado.'))
