# Viajeros Garabato Penido

Primera versión de una herramienta familiar para preparar búsquedas de vuelos. Interfaz adaptable a móvil, en español, sin dependencias ni servicios de pago.

## Abrir

Abre `index.html` en el navegador. También puedes servir esta carpeta con `python3 -m http.server 8000` y visitar `http://localhost:8000`. No requiere instalación ni claves. Publicación autorizada en GitHub Pages: https://albertogarabato.github.io/viajeros-garabato-pedido/ (rama main, carpeta raíz).

## Incluido

- SCQ, LCG, VGO, OPO y MAD seleccionados inicialmente; selección múltiple.
- Cinco viajeros por defecto, modificable entre 1 y 9. No se presuponen edades: confirmar adultos, menores y edades en el proveedor.
- Destino libre; ida y vuelta con flexibilidad de 0, ±1, ±3 o ±7 días en ambas fechas. Descarta fechas pasadas y vueltas anteriores a la salida.
- Generación de combinaciones de fechas y consultas externas de texto a Google Travel por aeropuerto. Las preferencias low cost y billetes independientes se añaden a la consulta; no son filtros garantizados del proveedor. Verificar siempre las condiciones allí.
- Exportación del plan en JSON. No se guardan automáticamente preferencias ni presupuestos.

## Límites de esta versión

No hay acceso a inventario de aerolíneas, búsqueda automática de rutas, precios en directo, reservas ni alertas automáticas de precio. Ningún enlace garantiza disponibilidad, una conexión o una tarifa para los cinco. Para comparar, usar el mismo destino, fechas y viajeros, e incluir todos los tramos de ida y vuelta. No hay conversión de moneda. La diferencia no valora el riesgo económico de una conexión perdida.

## Privacidad y coste

Sin Gmail, analítica, cookies, cuentas, APIs de pago, fuentes remotas ni secretos en el frontend. Las consultas externas se envían al buscador solo al pulsar sus enlaces; sus políticas se aplican allí. Los datos descargados permanecen bajo control de la familia. No introducir datos personales o credenciales en los campos. El funcionamiento local no tiene coste de servicio. El propietario autorizó hacer público el repositorio y activar GitHub Pages el 6 de noviembre de 2026. No introducir secretos ni presupuestos personales en el repositorio. Los formularios no envían sus valores a GitHub; los enlaces externos envían la consulta al buscador.

## Comprobar

Con Node instalado: `node tests/core.test.cjs`. Comprueba aritmética familiar, redondeo, combinaciones y validaciones de fechas e importes. Revisar también en navegador móvil después de cada cambio visual.

## Próximas iteraciones

1. Probar el flujo con presupuestos reales y confirmar distribución de adultos/menores y equipaje habitual.
2. Validar visualmente y con teclado en móvil; ajustar la experiencia con el uso familiar.
3. Valorar importación manual de presupuestos con fuente, fecha y tramos, sin datos personales.
4. Estudiar fuentes de datos autorizadas y gratuitas antes de integrar cualquier proveedor. Si una integración necesita secretos, deben vivir en un backend, nunca en estos archivos. No habilitar gastos ni despliegues automáticamente.

## Diseño

Interfaz adaptada a la referencia familiar: paisaje alpino, azul, cabecera manuscrita y buscador central. Consulta `DESIGN.md` para la procedencia del fondo y el alcance. Añadido un filtro opcional de duración en días. Favoritos y viajes guardados siguen pendientes y aparecen desactivados. El alcance es exclusivamente vuelos; se excluyen gastos terrestres.

La calculadora manual de presupuestos se retiró por petición del propietario. La comparación automática de ahorro, tiempo y riesgo se integrará con los resultados reales, cuando exista una fuente válida.
