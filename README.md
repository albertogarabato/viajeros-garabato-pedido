# Viajeros Garabato Pedido

Primera versión de una herramienta familiar para preparar búsquedas y comparar presupuestos de vuelos. Interfaz adaptable a móvil, en español, sin dependencias ni servicios de pago.

## Abrir

Abre `index.html` en el navegador. También puedes servir esta carpeta con `python3 -m http.server 8000` y visitar `http://localhost:8000`. No requiere instalación ni claves. No se ha desplegado ni publicado una web.

## Incluido

- SCQ, LCG, VGO, OPO y MAD seleccionados inicialmente; selección múltiple.
- Cinco viajeros por defecto, modificable entre 1 y 9. No se presuponen edades: confirmar adultos, menores y edades en el proveedor.
- Destino libre; ida y vuelta con flexibilidad de 0, ±1, ±3 o ±7 días en ambas fechas. Descarta fechas pasadas y vueltas anteriores a la salida.
- Generación de combinaciones de fechas y consultas externas de texto a Google Travel por aeropuerto. Las preferencias low cost y billetes independientes se añaden a la consulta; no son filtros garantizados del proveedor. Verificar siempre las condiciones allí.
- Exportación del plan en JSON. No se guardan automáticamente preferencias ni presupuestos.
- Comparación de dos presupuestos introducidos manualmente: precio por persona de todos los vuelos × viajeros + equipaje/asientos + traslados/aparcamiento + alojamiento/otros. Los extras son totales familiares. Todos los importes en EUR.
- Diferencia familiar y por persona; avisos de billetes separados.

## Límites de esta versión

No hay acceso a inventario de aerolíneas, búsqueda automática de rutas, precios en directo, reservas ni alertas automáticas de precio. Ningún enlace garantiza disponibilidad, una conexión o una tarifa para los cinco. Para comparar, usar el mismo destino, fechas y viajeros, e incluir todos los tramos de ida y vuelta. No hay conversión de moneda. La diferencia no valora el riesgo económico de una conexión perdida.

## Privacidad y coste

Sin Gmail, analítica, cookies, cuentas, APIs de pago, fuentes remotas ni secretos en el frontend. Las consultas externas se envían al buscador solo al pulsar sus enlaces; sus políticas se aplican allí. Los datos descargados permanecen bajo control de la familia. No introducir datos personales o credenciales en los campos. El funcionamiento local no tiene coste de servicio. Mantener este repositorio privado; no activar Pages, hosting ni cambiar visibilidad sin consultar al propietario.

## Comprobar

Con Node instalado: `node tests/core.test.cjs`. Comprueba aritmética familiar, redondeo, combinaciones y validaciones de fechas e importes. La interfaz requiere además revisión en navegador móvil.

## Próximas iteraciones

1. Probar el flujo con presupuestos reales y confirmar distribución de adultos/menores y equipaje habitual.
2. Validar visualmente y con teclado en móvil; ajustar la experiencia con el uso familiar.
3. Valorar importación manual de presupuestos con fuente, fecha y tramos, sin datos personales.
4. Estudiar fuentes de datos autorizadas y gratuitas antes de integrar cualquier proveedor. Si una integración necesita secretos, deben vivir en un backend, nunca en estos archivos. No habilitar gastos ni despliegues automáticamente.
