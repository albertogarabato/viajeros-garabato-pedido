# SerpApi — primera conexión validada

Comprobación realizada el **7 de noviembre de 2026**.

- Autenticación por API correcta.
- Cuenta activa con Free Plan de 0 €, 250 consultas mensuales.
- Una consulta técnica Madrid–Barcelona, solo ida, 15/02/2027, un adulto y vuelos directos: respuesta Success, 21 opciones con precio.
- Normalización posterior de esas 21 opciones sin repetir la petición.
- Prueba inicial: 1 búsqueda utilizada y 249 disponibles.
- Integración posterior en Cloudflare y GitHub Pages: 36 opciones de ida y 25 de vuelta, BCN 15–20/02/2027, cinco orígenes y categorías 2 adultos/3 niños. Dos consultas adicionales; comprobación posterior: 3 utilizadas, 247 disponibles, plan gratuito activo.

No es una propuesta de viaje familiar. La clave, las respuestas brutas y los datos privados de cuenta no están en este repositorio. La copia local de la clave queda fuera de la carpeta publicada, con permisos solo para el propietario; el servicio web la utiliza como secreto cifrado de Cloudflare.

## Implementado

`serpapi_flights.py`: comprobación de plan gratuito y cuota antes de cada búsqueda, máximo local configurable (cinco por defecto), ausencia de reintentos, caché en memoria de 15 minutos y eliminación de duplicados. Las claves se envían únicamente a serpapi.com por HTTPS; no se imprimen ni se devuelven al navegador. Las redirecciones del transporte están bloqueadas.

`check_serpapi.py`: lee `SERPAPI_API_KEY` del entorno del backend. Sin argumentos consulta solo un resumen de cuenta sin clave ni correo. Para una única búsqueda acotada permite `--origin`, `--destination`, `--date`, `--adults` y `--children`. Nunca poner la clave como argumento del comando.

El límite por instancia no sustituye a la cuota del proveedor ni al presupuesto persistente que deberá tener el servidor compartido. Un backend público requiere autenticación o control de acceso, límites persistentes, caché compartida y protección frente al agotamiento de la cuota.

## Límites pendientes

- Es una API de terceros sobre resultados de Google Flights, no una API oficial de Google ni cobertura de todas las aerolíneas.
- Los importes se conservan como precios observados de la consulta, sin multiplicarlos por el número de viajeros. Antes de habilitar el total familiar hay que comprobar la base del precio con el grupo real y sus categorías de edad.
- Los suplementos de equipaje y la protección de las conexiones no se presuponen incluidos.
- Las horas recibidas son locales; hay que resolver zonas horarias antes de introducir vuelos en el optimizador.
- Las ofertas llevan `status: observed` y no se marcan como cotizaciones verificadas del motor. Plazas y precios pueden cambiar antes de reservar.
- El servicio de primera fuente está desplegado y conectado a GitHub Pages, con acceso familiar obligatorio. Devuelve precios observados; todavía no alimenta el motor de cotizaciones verificadas. Ver `../../cloudflare/README.md`.
- Hay 39 pruebas de backend con datos sintéticos; la validación de conexión descrita arriba fue una petición real independiente.

## Referencias

[Plan gratuito](https://serpapi.com/pricing), [parámetros de vuelos](https://serpapi.com/google-flights-api), [consulta de cuenta](https://serpapi.com/account-api).
