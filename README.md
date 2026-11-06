# Viajeros Garabato Penido

Aplicación familiar centrada exclusivamente en vuelos. Publicada en https://albertogarabato.github.io/viajeros-garabato-pedido/ con autorización del propietario. El identificador histórico del repositorio y del enlace conserva «pedido».

## Estado actual

Interfaz en español, adaptable a móvil y basada en la referencia familiar de montaña y lago. SCQ, LCG, VGO, OPO y MAD seleccionados por defecto; cinco viajeros modificables; destino, fechas flexibles y filtro de duración.

«Buscar» conserva la consulta en la página. No abre Google Flights ni otro buscador. Como todavía no hay proveedor ni servicio de búsqueda desplegado, muestra **búsqueda de precios no disponible**, sin inventar ofertas ni afirmar que no existen vuelos. No se guardan preferencias ni se envían consultas a otros servicios en esta configuración.

No hay calculadora manual, servicios complementarios ni gastos terrestres. Los apartados pendientes aparecen desactivados.

## Motor y conexión

`backend/optimizer.py` contiene el primer núcleo de exploración de rutas directas y con una conexión, cruce de horarios, cotizaciones del grupo y alternativas de precio/tiempo/riesgo. Tiene 19 pruebas con datos exclusivamente sintéticos. No está conectado a la interfaz ni a una fuente real.

`search-client.js` prepara el contrato de búsqueda HTTPS. El metadato `flight-search-api` está vacío intencionadamente; no incluye claves. Una integración real requiere un backend, fuente autorizada, adultos y edades de menores, y validación de las ofertas. No basta con rellenar una URL. GitHub Pages sirve la interfaz estática, no ejecuta el motor Python.

Consulta `backend/README.md`, `backend/FUENTES.md` y `REQUISITOS.md` para alcance, limitaciones y próximos pasos. `DESIGN.md` documenta el fondo y la referencia visual.

## Uso local y comprobaciones

Abre `index.html` para revisar la interfaz sin instalación. Para desarrollo también puedes servir la carpeta con `python3 -m http.server 8000`.

- Fechas y sintaxis: `node tests/core.test.cjs`.
- Motor: `python3 -m unittest discover -s backend/tests -v`.
- Verificar además el flujo en navegador y móvil después de cambios de interfaz.

## Coste y seguridad

Sin Gmail, seguimiento, APIs de pago, secretos en el frontend ni compras automáticas. No se han creado cuentas ni activado facturación. Antes de habilitar una fuente hay que comprobar sus condiciones, cobertura y coste cero efectivo. Los precios actuales de low cost siguen siendo el principal acceso pendiente.
