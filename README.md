# InstarApp
Una red social para instar la conexión entre personas

## Versión final integrada

Se unificaron «Poyecto red social» y «Poyecto red social - copia».
La versión con comentarios y moderación aporta el código de la aplicación;
se conservan también los archivos e imágenes adicionales de la copia.

El diseño usa un único archivo `static/css/estilos.css` e íconos SVG locales
en `static/icons/`. No se agregaron funciones, secciones ni textos a las páginas.
El CSS adapta los formularios, botones y publicaciones a celulares y escritorio.

Cambios de integración autorizados:

- Corrección del parámetro del perfil y recuperación del manejo de errores de
  publicación que ya existía en la copia, evitando una definición duplicada.
- Estructura HTML básica y enlace al CSS en comentarios y moderación.
- Migración de los cuatro campos de moderación que ya estaban declarados en
  los modelos. Se aplicó únicamente a la base de esta entrega, conservando datos.
- Recuperación de los mensajes del perfil que estaban presentes en la copia.

## Abrir en esta computadora

Abrí PowerShell en esta carpeta (la que contiene `manage.py`) y ejecutá:

```powershell
& 'C:\Users\Pc\Documents\Poyecto red social\InstarApp\env\Scripts\python.exe' manage.py runserver
```

Luego abrí http://127.0.0.1:8000/ en el navegador.
Este comando reutiliza el entorno de Python que ya tenés instalado.
Las plantillas de Django se abren a través de este servidor.

## Usar en otra computadora

Con Python compatible con Django 6.1 instalado, desde esta carpeta:

```powershell
python -m venv env
.\env\Scripts\python.exe -m pip install -r requirements.txt
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py runserver
```

El entorno virtual no se incluye porque depende de la instalación de Python de
cada equipo. La base SQLite y las imágenes sí están incluidas.

## Verificación

- Las ocho pruebas existentes del proyecto pasan.
- Django no informa problemas de configuración ni migraciones pendientes.
- Las siete plantillas generan HTML correctamente con el CSS enlazado.
- Todos los SVG referenciados por el CSS están incluidos.
- Los datos de todas las tablas originales se conservaron.
- No fue posible comprobar visualmente las páginas: el navegador sin interfaz
  se cerró antes de generar las capturas. La adaptación visual queda sin verificar.
