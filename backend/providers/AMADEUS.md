# Primera conexión: Amadeus TEST

Adaptador de servidor: `amadeus_test.py`. Comprobación: `../check_amadeus.py`.

## Estado

Implementados autenticación OAuth, reutilización temporal del token, consulta de tramos directos por aeropuerto, normalización de tarifas totales del grupo y límites locales de peticiones. 10 pruebas del adaptador y 19 del motor, con transporte y datos sintéticos. **Pendiente de probar contra Amadeus con una cuenta Test del propietario.**

El destino se indica al ejecutar la comprobación; no está prefijado. Una ejecución consulta SCQ, LCG, VGO, OPO y MAD para una fecha, con máximo seis peticiones contando autenticación. No hace barridos de fechas ni reintentos automáticos. El límite es por ejecución, no sustituye al control de cuota mensual.

## Cuenta y credenciales

1. Crear una cuenta en https://developers.amadeus.com/ y verificarla.
2. Crear una aplicación en el espacio Self-Service, entorno Test.
3. Mantener las credenciales Test fuera del repositorio y del frontend. El adaptador lee `AMADEUS_TEST_API_KEY` y `AMADEUS_TEST_API_SECRET` del entorno del servidor. No pegarlas en el chat ni en argumentos de comandos.
4. No solicitar producción ni proporcionar datos de facturación en esta fase.

## Comprobar

Desde la raíz del proyecto, una vez configuradas las variables de forma privada:

```sh
python3 backend/check_amadeus.py --destination CODIGO_IATA --date AAAA-MM-DD --adults NUMERO --child-ages EDADES
```

Sustituir los parámetros por una consulta elegida para probar; omitir `--child-ages` cuando no haya menores. Las edades son las que tendrán en la fecha de salida. El adaptador traduce a categorías Amadeus: adulto desde 12 años, niño de 2 a 11, bebé menor de 2. El usuario debe confirmar estas categorías y las condiciones de la compañía antes de cualquier uso real.

## Límites que no hay que ocultar

- Host fijado a `test.api.amadeus.com`. No hay opción de producción, reserva ni cobro en este código.
- Todas las ofertas llevan `status: test` y `eligibleForLiveRanking: false`. El frontend de precios reales no debe mostrarlas como vuelos disponibles para comprar.
- El entorno Test tiene datos limitados; una respuesta vacía no implica que no haya vuelos.
- Amadeus Self-Service no aporta la cobertura low cost que necesita este proyecto. Es una primera prueba de integración, no la solución completa.
- En esta fase se consultan tramos directos. No se divide el precio de un itinerario con conexión para inventar precios individuales.
- Las horas recibidas se conservan como horas locales. Antes de utilizarlas en el motor hay que resolver zonas horarias por aeropuerto. No se infiere UTC ni un desfase fijo.
- El equipaje incluido se conserva por viajero cuando viene informado; suplementos desconocidos no se tratan como coste cero.
- No se han desplegado un backend ni un endpoint público. La web seguirá mostrando indisponibilidad de precios reales hasta completar una integración válida.

## Documentación primaria

- [Especificación oficial Flight Offers Search](https://github.com/amadeus4dev/amadeus-open-api-specification/blob/main/spec/json/FlightOffersSearch_v2_swagger_specification.json)
- [Guía oficial de vuelos](https://github.com/amadeus4dev/developer-guides/blob/master/docs/resources/flights.md)
- [FAQ: entorno Test, cobertura y facturación](https://admin.developers.amadeus.com/self-service/apis-docs/guides/developer-guides/faq/)
