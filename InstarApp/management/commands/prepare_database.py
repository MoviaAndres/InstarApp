from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = 'Prepara el esquema privado de Django en Supabase, sin borrar tablas.'

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            raise CommandError('Este comando requiere PostgreSQL y la configuración de producción.')
        with connection.cursor() as cursor:
            cursor.execute('CREATE SCHEMA IF NOT EXISTS instar')
            cursor.execute('REVOKE ALL ON SCHEMA instar FROM PUBLIC')
            cursor.execute("""
                DO $$ BEGIN
                    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                        REVOKE ALL ON SCHEMA instar FROM anon;
                    END IF;
                    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                        REVOKE ALL ON SCHEMA instar FROM authenticated;
                    END IF;
                END $$;
            """)
        self.stdout.write(self.style.SUCCESS('Esquema instar preparado.'))
