# Primera conexión web con SerpApi

Servicio creado el 7 de noviembre de 2026 en Cloudflare Workers:
`viajeros-garabato-penido-api.alberto-garabato.workers.dev`.

`worker.mjs` está desplegado. El endpoint `/health` confirmó por HTTPS el campo `version: 2026-11-07-source-2`. La clave SerpApi está cifrada como secreto en Cloudflare; el propietario ha guardado también el secreto familiar. `/health` confirma la configuración completa y `/search` devuelve 401 sin autorización. Prueba autenticada completada desde GitHub Pages: 36 opciones de ida y 25 de vuelta para la consulta técnica BCN 15–20/02/2027, con 2 adultos y 3 niños. La cuota posterior confirma tres consultas acumuladas (una previa más las dos del portal), 247 restantes y plan de precio cero.

## Configuración privada

En Variables and Secrets de Cloudflare, crear dos entradas de tipo **Secret**:

- `SERPAPI_API_KEY`: clave existente de SerpApi. Nunca guardarla aquí ni en GitHub.
- `FAMILY_ACCESS_CODE`: clave de acceso familiar de al menos doce caracteres, que debe escoger e introducir el propietario. Es distinta de la clave de SerpApi.

Si falta cualquiera de las dos, las búsquedas quedan bloqueadas. La clave familiar debe viajar en `Authorization: Bearer …`, nunca en una URL. No se imprimen claves ni respuestas completas de la fuente. El origen web permitido es únicamente el de la aplicación en GitHub Pages; la autenticación también es obligatoria para llamadas sin navegador.

## Alcance comprobable

- Dos consultas como máximo por búsqueda: ida y vuelta por separado, desde/hacia los cinco aeropuertos seleccionados, en fechas exactas, hasta una escala.
- Comprueba cuenta activa, precio del plan cero y cuota disponible antes de cada consulta. Sin reintentos automáticos, compras ni cambios de plan.
- Caché de quince minutos mediante Cache API de Workers; puede no compartirse entre ubicaciones. No es un contador global ni garantiza un máximo mensual propio. La cuota gratuita del proveedor sigue siendo el límite operativo.
- Devuelve solo campos permitidos, sin claves, enlaces de búsqueda con credenciales ni respuestas privadas del proveedor.
- Mantiene los importes como precios observados: no confirma su base por persona/grupo, no multiplica ni suma precios, no afirma disponibilidad para toda la familia ni una ruta óptima.
- Esta conexión no genera todavía combinaciones independientes ni explora fechas flexibles; lo declara expresamente en la respuesta.

## Pruebas sin consumir cuota

Importar `worker.test.mjs` con Node y ejecutar `runTests()`. Todas las respuestas son sintéticas. El adaptador Python mantiene sus propias pruebas. Para comprobar el despliegue, `/health` no consume consultas de SerpApi; una llamada sin autorización a `/search` tampoco debe consumirlas.

## Compatibilidad de transporte

Workers no admite `redirect: error`. El transporte usa `redirect: manual` y rechaza respuestas no satisfactorias; no sigue redirecciones que pudieran llevar la clave a otro servidor. La prueba de transporte exige esta opción. Los fallos de conexión se distinguen de los tiempos de espera sin devolver URLs ni detalles privados.
