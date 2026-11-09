# Publicar Instar con Netlify, Render y Supabase

La aplicación conserva Django y sus cuentas existentes. La configuración local
`INSTAR.settings` sigue usando SQLite y la carpeta media. Render usa
`INSTAR.production`, PostgreSQL y el almacenamiento S3 privado de Supabase.

## Preparar Supabase

1. Crear o seleccionar el proyecto. Elegir una región cercana al servidor.
2. En Storage, crear el bucket **privado** `instar-media`.
3. Generar las credenciales S3 y copiar endpoint, región y claves al entorno de
   Render. Las claves S3 nunca se guardan en Git ni en Netlify.
4. Desde Connect, copiar la cadena PostgreSQL del pooler en modo **Session**,
   con su host, usuario y puerto reales. Usar esa cadena como `DATABASE_URL`.

El comando `prepare_database` crea el esquema `instar` y restringe su acceso.
No agregar este esquema a los esquemas expuestos de la Data API. La autenticación
y las comprobaciones de permisos las sigue haciendo Django.

## Preparar Netlify

Importar el repositorio y usar su `netlify.toml`. La base de compilación es
`netlify`, el comando es `node build.mjs` y la salida es `public`.
Reservar el sitio para obtener su URL pública HTTPS.

En Netlify configurar únicamente `DJANGO_ORIGIN` con la URL HTTPS de Render.
El proceso genera una regla que reenvía las visitas al servidor Django.

## Crear el servicio Render

Importar el repositorio con el Blueprint `render.yaml`, o crear un Web Service:

- Python: la versión declarada en `.python-version`.
- Build: `bash build.sh`.
- Inicio: `python -m gunicorn INSTAR.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --access-logfile -`.
- Comprobación de salud: `/salud/`.
- Variables: las indicadas en `.env.production.example`.

Generar una `DJANGO_SECRET_KEY` nueva de al menos 50 caracteres. Poner la URL
reservada de Netlify en `PUBLIC_SITE_URL`. Render proporciona
`RENDER_EXTERNAL_HOSTNAME` automáticamente.

El build instala dependencias, recoge los archivos estáticos, prepara el esquema
privado y aplica las migraciones incluidas en Git. No usa la SQLite local.
Se deja desactivado el despliegue automático para controlar cuándo se publica.

El registro actual no utiliza correo. Si se agrega recuperación de contraseñas
u otro envío de emails, configurar SMTP con `EMAIL_HOST`, `EMAIL_PORT`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` y `DEFAULT_FROM_EMAIL`.

La configuración empieza con el plan Free de Render. Ese plan se suspende tras
15 minutos sin visitas y puede tardar alrededor de un minuto en despertar.
Como el proxy de Netlify tiene un límite de 26 segundos, una primera visita puede
requerir reintento. Para un servicio continuo hay que evaluar un plan que no se
suspenda; no se contrata un plan de pago automáticamente.

## Conservar los datos locales

Antes de copiar datos, evitar publicaciones nuevas durante la transferencia.
Ejecutar con el entorno local y **sin** `DJANGO_SETTINGS_MODULE=INSTAR.production`:

```powershell
python manage.py export_for_deploy --output data-export/primera-publicacion
```

La carpeta exportada contiene una copia SQLite, `datos.json`, recuentos y un
manifiesto de imágenes. Es privada y está excluida de Git. Incluye hashes de
contraseñas: no subirla al repositorio ni a la carpeta pública de Netlify.

Con las variables de producción cargadas de forma privada, importar en una base
nueva de destino, sin datos de usuarios previos:

```powershell
python manage.py loaddata data-export/primera-publicacion/datos.json --settings=INSTAR.production
python manage.py upload_deploy_media --manifest data-export/primera-publicacion/media-manifest.json --source media --settings=INSTAR.production
```

El segundo comando solo comprueba archivos. Agregar `--upload` cuando se vaya a
transferirlos. Ante faltantes se debe restaurar el archivo o aceptar expresamente
su omisión con `--allow-missing`. Los nombres se conservan y no se sobrescriben
objetos existentes.

Si el equipo local no puede cargar el controlador de PostgreSQL, se puede hacer
la primera importación desde Render: copiar `datos.json` a un objeto de nombre
único dentro del bucket **privado**, configurar ese nombre en
`BOOTSTRAP_FIXTURE_KEY` y desplegar. `bootstrap_data` solo importa si aún no hay
cuentas; no sobrescribe datos existentes. El objeto conserva su acceso privado
y no se publica en GitHub ni en Netlify. Después de verificar los datos, quitar
la variable de importación del entorno.

Finalmente comparar los recuentos, probar login, búsqueda, imágenes y una
publicación de prueba, y comprobar que `/salud/` responde correctamente.

## Referencias

- https://render.com/docs/deploy-django
- https://render.com/docs/free
- https://supabase.com/docs/guides/database/connecting-to-postgres
- https://supabase.com/docs/guides/storage/s3/authentication
- https://docs.netlify.com/manage/routing/redirects/rewrites-proxies/
