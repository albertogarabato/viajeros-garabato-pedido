# Viajeros Garabato Penido

Portal familiar exclusivamente de vuelos. Publicado con autorización en https://albertogarabato.github.io/viajeros-garabato-pedido/ (el enlace conserva el nombre histórico «pedido»).

## Primera conexión web: versión 0.3.0

- Orígenes SCQ, LCG, VGO, OPO y MAD; destino por código IATA o una ciudad de la lista local.
- Composición de viajeros explícita: adultos de 12 años o más, niños de 2–11, bebés con asiento o en brazos. Los valores iniciales deben confirmarse.
- Cloudflare Workers aloja la conexión con SerpApi. La clave del proveedor solo está en un secreto del servidor. Las búsquedas requieren además una clave familiar privada.
- Los resultados aparecen en la página; se consultan ida y vuelta por separado, en fechas exactas, con hasta una escala. Hasta dos consultas al proveedor por búsqueda, salvo respuestas en caché. Cada intento fallido puede afectar a la cuota del proveedor.
- Se pueden ordenar por precio mostrado o duración. No hay afirmación de mejor ruta global ni cotización familiar confirmada. El precio se conserva tal como llega; no se multiplica ni se suman ida y vuelta mientras no se verifique su base.
- Cobertura limitada a Google Flights a través de SerpApi. No abarca todas las aerolíneas. Equipaje, plazas, condiciones y protección de las conexiones requieren comprobación.

Las fechas flexibles y la construcción de conexiones con billetes independientes todavía no están conectadas a datos reales. Se muestran como pendientes. No hay hoteles, calculadora manual ni costes de desplazamientos terrestres.

## Despliegue y seguridad

`cloudflare/worker.mjs` se desplegó el 7/11/2026 en `https://viajeros-garabato-penido-api.alberto-garabato.workers.dev` con versión `2026-11-07-source-1`. `/health` verifica la versión y si existen ambos secretos; no consume cuota de vuelos. La clave SerpApi está guardada cifrada. El propietario ha guardado `FAMILY_ACCESS_CODE` cifrado; `/health` confirma ambos secretos configurados y `/search` rechaza peticiones sin autorización (401). Aún falta una búsqueda autenticada desde el portal para verificar el recorrido completo.

`search-client.js` usa el servicio HTTPS configurado en `index.html`. La clave familiar se introduce en el formulario, se mantiene en memoria de la página y no se guarda en almacenamiento del navegador. Nunca introducir allí la clave de SerpApi.

No se han activado planes de pago ni compras. El servicio comprueba que SerpApi siga siendo una cuenta gratuita activa y tenga cuota antes de consultar. Caché de quince minutos por ubicación, sin garantía de caché global ni contador mensual propio. No hay Gmail, nombres, documentos ni reservas automáticas.

## Motor de rutas pendiente de conexión

`backend/optimizer.py` contiene el núcleo de combinación de vuelos con horarios absolutos, cotizaciones del grupo y alternativas de precio, tiempo y riesgo. Tiene 19 pruebas sintéticas y no está conectado todavía a la interfaz. La conexión web actual utiliza precios observados; no los convierte en cotizaciones confirmadas de ese motor.

La fuente Amadeus Self-Service se retiró el 17/07/2026. Su adaptador real permanece deshabilitado; se conservan pruebas simuladas. No crear cuentas para esa integración retirada.

## Comprobaciones

- `python3 -m unittest discover -s backend/tests -v`: 39 pruebas sintéticas.
- Importar `cloudflare/worker.test.mjs` con Node y ejecutar `runTests()`: 28 comprobaciones sintéticas de autenticación, validación, límites de plan y filtrado de datos, sin consumir cuota.
- `node tests/core.test.cjs`: fechas y sintaxis.
- Revisar formulario y presentación en navegador después de cambios.

La consulta técnica original de SerpApi devolvió 21 opciones. Se ha vuelto a usar esa respuesta de forma local para verificar la normalización, sin nuevas búsquedas. Consultar `cloudflare/README.md`, `backend/providers/SERPAPI.md`, `REQUISITOS.md` y `DESIGN.md` para detalles.
