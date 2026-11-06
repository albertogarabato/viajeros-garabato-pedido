# Motor Garabato — primera pieza del backend

Este motor es independiente del destino: no contiene rutas prefijadas a Varsovia ni a ninguna otra ciudad. El frontend publicado todavía prepara consultas externas. Este código no se ejecuta en GitHub Pages, que sirve archivos estáticos. No hay proveedor de tarifas conectado ni backend desplegado.

## Implementado

- `discover_paths`: construye alternativas directas y de una conexión a partir de una red de rutas dirigida suministrada por una fuente. No inventa la ruta inversa.
- `search_one_way`: cruza ofertas de tramos individuales desde todos los orígenes seleccionados. Puede descubrir una combinación barata que no aparece como itinerario completo en un proveedor.
- Compara horas con zona horaria, incluidos cambios de fecha. Rechaza enlaces en aeropuertos distintos y conexiones por debajo del margen configurable. Margen inicial de cribado: 180 minutos; no es una garantía ni el tiempo mínimo oficial de un aeropuerto.
- Las ofertas deben corresponder al grupo exacto de adultos y edades de menores, con precio total familiar, misma moneda y misma modalidad de equipaje. Nunca multiplica una plaza barata por cinco para simular disponibilidad.
- Filtra tarifas de prueba, históricas, indicativas, caducadas y demasiado antiguas. Una fuente de rutas no basta para verificar horarios o precios.
- Suma los precios de los tramos, conserva las alternativas de precio/tiempo/riesgo y destaca la más económica y la más rápida. No asigna arbitrariamente una puntuación de «mejor».
- Calcula el ahorro familiar por hora adicional respecto de una alternativa más rápida especificada, si hay ahorro positivo.
- `round_trips`: combina las idas y vueltas obtenidas por separado, exigiendo el mismo aeropuerto de origen y destino. No presume vuelos de regreso ni cambios entre aeropuertos de una misma ciudad.
- Límites de trabajo explícitos: si se alcanzan, devuelve un error y no afirma haber encontrado el mínimo global. Sin límite rígido universal de duración del viaje.

## Qué falta

Una fuente autorizada que suministre rutas vigentes, horarios y tarifas para el grupo. Los adaptadores de proveedor serán responsables de traducir los datos y comprobar que una oferta marcada como `live` incluye realmente esos viajeros y ese equipaje. El motor no puede certificar una afirmación falsa del proveedor.

Después: orquestador de consultas con caché y cuotas, servicio HTTPS con claves fuera del navegador, integración de resultados con la interfaz y tratamiento de itinerarios protegidos ofrecidos como una reserva completa. En esta primera pieza, dos ofertas de un tramo combinadas son siempre billetes independientes, incluso si pertenecen a la misma compañía.

No se ha activado ningún servicio, cuenta, facturación ni API. No hay acceso a claves del usuario.

## Comprobar

Desde la raíz del proyecto:

```sh
python3 -m unittest discover -s backend/tests -v
```

Las 19 pruebas usan aeropuertos AAA/BBB/CCC/DDD y precios **sintéticos exclusivamente para validar el algoritmo**. No se muestran en la aplicación ni son resultados de viajes reales.

## Contrato de los datos

`Flight` representa un vuelo dirigido y una cotización para el grupo completo. Debe tener identificador y proveedor; aeropuertos IATA exactos; salida/llegada con zona horaria; total en unidades menores de la moneda (céntimos en EUR); adultos y edades; modalidad de equipaje; fecha de consulta y caducidad. El enlace de reserva, cuando exista, procede del proveedor. Se deben volver a comprobar las ofertas antes de reservar: las sumas de billetes independientes no son una reserva conjunta ni bloquean plazas.

Las búsquedas solo pueden ser completas dentro de las fuentes, fechas y vuelos que se hayan consultado. No hay promesa de mínimo global de todas las aerolíneas.
