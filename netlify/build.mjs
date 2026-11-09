import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const input = process.env.DJANGO_ORIGIN;
if (!input) throw new Error('Configurá DJANGO_ORIGIN con la dirección HTTPS del servicio Render.');
const url = new URL(input);
if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
  throw new Error('DJANGO_ORIGIN debe ser un origen HTTPS sin rutas ni credenciales.');
}
const directory = fileURLToPath(new URL('./public/', import.meta.url));
await mkdir(directory, { recursive: true });
await writeFile(directory + '/_redirects', `/* ${url.origin}/:splat 200!\n`);
await writeFile(directory + '/index.html', '<!doctype html><html lang="es"><meta charset="utf-8"><title>Instar</title></html>\n');
console.log('Entrada de Netlify preparada.');
