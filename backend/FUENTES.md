> Corrección: Amadeus Self-Service está retirado desde el 17/07/2026. Las referencias antiguas a cuotas y registro no representan una oferta vigente. No se recomienda crear una cuenta ni usar ese adaptador.

# Validación de fuentes — 6 de noviembre de 2026

Objetivo: buscar tramos separados y combinarlos, para cualquier destino, desde SCQ, LCG, VGO, OPO y MAD. No es una búsqueda de un viaje concreto.

## Resultado de la revisión

No se ha validado todavía una fuente que reúna acceso personal autorizado, tarifas actuales para el grupo, cobertura low cost suficiente y ausencia de facturación. Conectar tres APIs que no cumplan esas condiciones no resuelve la carencia.

| Fuente | Evidencia | Decisión inicial |
|---|---|---|
| Aena | Publica destinos a partir de programación actual y advierte de posibles cambios. No da una tarifa para cinco personas ni confirma una conexión en una fecha. | Referencia para validar la red; pendiente de mecanismo autorizado de actualización. |
| Aeropuerto de Oporto | Tiene directorio de destinos y aerolíneas. | Misma función: red, sin tomarla como cotización. |
| Amadeus Self-Service | El portal oficial anuncia su retirada el 17/07/2026; la organización de SDK oficiales está archivada. | Descartado para nuevas integraciones. Conector deshabilitado. |
| Skyscanner Travel API | Acceso comercial sujeto a selección; excluye personas con uso no comercial y exige audiencia. | No es una vía de acceso para este proyecto familiar. |
| Travelpayouts Data API | Datos en caché de búsquedas previas. La API de búsqueda en directo requiere acceso separado. | No sirve por sí sola para confirmar disponibilidad del grupo ni clasificar como precio actual. |
| Duffel | Publica cargo por exceso de búsquedas respecto a reservas. | No activar bajo la política de coste cero. |
| Aerolíneas low cost | Sus páginas públicas pueden ayudar a investigar rutas. No se ha verificado acceso automatizado de producción para este proyecto. | No se han usado endpoints internos ni contratado intermediarios. Investigar acceso autorizado antes de integrar. |

## Fuentes primarias

- [Aena — Santiago](https://www.aena.es/es/santiago-rosalia-de-castro/aerolineas-y-destinos/destinos-aeropuerto.html)
- [Aena — A Coruña](https://www.aena.es/es/a-coruna/aerolineas-y-destinos/destinos-aeropuerto.html)
- [Aena — Vigo](https://www.aena.es/es/vigo/aerolineas-y-destinos/destinos-aeropuerto.html)
- [Aena — Madrid](https://www.aena.es/es/adolfo-suarez-madrid-barajas/aerolineas-y-destinos/destinos-aeropuerto.html)
- [Oporto — destinos](https://www.portoairport.pt/en/opo/flights-destinations/airlines/airlines-and-destinations)
- [Amadeus — FAQ de cobertura, pruebas y facturación](https://admin.developers.amadeus.com/self-service/apis-docs/guides/developer-guides/faq/)
- [Skyscanner — criterios de acceso](https://www.partners.skyscanner.net/contact/travel-api)
- [Travelpayouts — documentación de datos en caché](https://travelpayouts.github.io/slate/)
- [Duffel — precios](https://duffel.com/pricing)
- [Ryanair — condiciones de uso](https://www.ryanair.com/gb/en/lp/legal/terms-of-use)

## Siguiente prueba de integración

Conseguir acceso autorizado a una fuente viable y comprobar: tramos individuales, ambas direcciones, precio para todo el grupo, fechas, equipaje, vigencia y cuotas sin gasto. Solo entonces conectar ese proveedor al motor y al frontend. El diseño admite varias fuentes; no presupone que todas ofrezcan la misma cobertura.
