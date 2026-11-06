> Referencia funcional aportada por el propietario el 6 de noviembre de 2026. No describe todas las funciones implementadas.
> Correcciones posteriores: nombre **Viajeros Garabato Penido**; **solo vuelos**, sin servicios adicionales ni gastos terrestres.
> El propietario autorizó posteriormente repositorio público y publicación gratuita en GitHub Pages. Se conserva el enlace con el identificador original.
> Estado actual: interfaz, consultas externas asistidas. Calculadora manual retirada por el propietario. Pendientes: motor automático, fuentes reales, persistencia, múltiples destinos, aeropuertos adicionales, regreso abierto y configuración de adultos/menores.

# VIAJEROS GARABATO PENIDO
## Documento de definición funcional y arquitectura — v0.6
**Fecha:** 6 de noviembre de 2026  
**Estado:** Requisitos definidos. Pendiente de desarrollo e integración con fuentes reales.

### 1. Objetivo del proyecto

Desarrollar una aplicación web familiar, privada y sencilla que permita buscar y comparar vuelos de distintas aerolíneas, incluyendo compañías tradicionales y low cost.

El objetivo principal NO es crear otro Skyscanner, sino desarrollar un **motor de búsqueda y optimización personalizado** capaz de explorar automáticamente combinaciones de aeropuertos, fechas, rutas y escalas para descubrir oportunidades de ahorro que no resultan evidentes en las búsquedas convencionales.

El proyecto es exclusivamente familiar. No contemplar por ahora comercialización, monetización, usuarios externos ni funcionalidades empresariales.

**Principios fundamentales:**
- Coste de funcionamiento inicial: 0 €.
- Nunca activar servicios de pago sin autorización expresa.
- Priorizar cobertura amplia, aunque las búsquedas tarden más.
- Optimizar el precio total para la familia.
- Mostrar precios reales y verificables, nunca inventados.
- Diseñar una interfaz moderna, sencilla y adaptada a móviles.

### 2. Configuración familiar

**Aeropuertos de salida preseleccionados:**

| Código | Aeropuerto |
|---|---|
| SCQ | Santiago de Compostela |
| LCG | A Coruña |
| VGO | Vigo |
| OPO | Oporto |
| MAD | Madrid-Barajas |

Los cinco aeropuertos deben aparecer seleccionados por defecto. El usuario podrá desmarcarlos o añadir otros aeropuertos internacionales.

Madrid se incluye porque es posible desplazarse desde Santiago en tren de alta velocidad. Oporto también resulta accesible en coche.

**Importante:** NO calcular ni añadir gastos terrestres de desplazamiento a los aeropuertos. Quedan expresamente excluidos combustible, aparcamiento, tren, AVE, peajes y otros costes similares.

Los cinco aeropuertos competirán en igualdad de condiciones.

**Viajeros:** cinco por defecto, con posibilidad de modificar el número y configurar adultos y menores.

### 3. Funcionalidades del buscador

**Orígenes y destinos**
- Uno o varios aeropuertos de origen.
- Uno o varios destinos.
- Modo «Cualquier destino».
- Aeropuerto de regreso diferente del de salida.
- Posibilidad de descubrir aeropuertos alternativos.

**Fechas**
- Fechas exactas.
- Intervalos flexibles de salida y regreso.
- Duración mínima y máxima del viaje.
- Búsqueda del mes o fechas más económicas.
- Comparación automática de combinaciones de fechas.

**Aerolíneas**
- Compañías tradicionales.
- Compañías low cost, especialmente Ryanair, Wizz Air, Vueling, easyJet, Transavia y Volotea.
- Posibilidad de combinar distintas aerolíneas.

**Conexiones**
Se permiten tres modalidades:
1. Vuelos directos o conexiones protegidas por la aerolínea.
2. Autoconexiones con protección comercial específica, si existe.
3. Billetes independientes sin protección.

No excluir los billetes independientes. Mostrar claramente sus riesgos, márgenes de conexión, necesidad de recoger equipaje y realizar una nueva facturación.

**Tarifas**
- Precio individual y precio total familiar.
- Tarifa básica y tarifa con equipaje.
- Indicar cuándo los suplementos de equipaje no estén disponibles.
- Mostrar moneda, proveedor y fecha de consulta.
- Diferenciar precios actuales verificables de precios históricos o indicativos.

### 4. Motor de optimización Garabato

El criterio elegido es **valoración flexible del ahorro familiar**.

No imponer un límite rígido universal de duración del vuelo. El algoritmo debe evaluar si el ahorro justifica las horas adicionales de viaje.

Ejemplo hipotético:

- Vuelo A: 3.500 € para cinco personas, 9 horas.
- Vuelo B: 2.500 € para cinco personas, 13 horas.
- Ahorro familiar: 1.000 €.
- Tiempo adicional: 4 horas.
- Indicador: 250 € de ahorro familiar por hora adicional.

Este indicador será informativo, no el único criterio de clasificación.

El algoritmo debe considerar:
- Precio total familiar.
- Duración total del itinerario.
- Tiempo y número de escalas.
- Riesgo de conexiones independientes.
- Equipaje y suplementos.
- Horarios de salida y llegada.
- Disponibilidad para todos los viajeros.
- Fiabilidad y vigencia del precio.

Presentar, al menos, tres resultados destacados:
- Más económico.
- Mejor equilibrio entre ahorro, duración y riesgo.
- Más rápido.

Aplicar también un criterio de dominancia para relegar opciones más caras y lentas sin ventajas relevantes.

### 5. Exploración inteligente de rutas

Esta es una de las funcionalidades más importantes del proyecto.

El buscador no debe limitarse a consultar itinerarios completos ofrecidos por un único proveedor.

Debe poder descubrir conexiones alternativas entre aeropuertos.

**Ejemplo: Santiago → Bucarest**

Investigar automáticamente posibilidades como:
- Santiago → Madrid → Bucarest.
- Santiago → Alicante → Bucarest.
- Santiago → Barcelona → Bucarest.
- Madrid → Bucarest.
- Oporto → Bucarest.
- Otras conexiones que aparezcan en los datos disponibles.

Estos itinerarios son ejemplos de exploración, no rutas ni disponibilidades confirmadas.

Utilizar un modelo de red de aeropuertos y rutas, donde los aeropuertos son nodos y los vuelos son conexiones.

Primero identificar combinaciones prometedoras y después consultar horarios, precios y disponibilidad.

Evitar búsquedas masivas innecesarias que agoten cuotas gratuitas.

### 6. Arquitectura técnica

```text
┌────────────────────────────────────┐
│       APLICACIÓN WEB / PWA         │
│                                    │
│  Interfaz familiar                 │
│  Selección de aeropuertos          │
│  Destinos y fechas flexibles       │
│  Viajeros y equipaje               │
│  Resultados y comparaciones        │
└─────────────────┬──────────────────┘
                  │ HTTPS
                  ▼
┌────────────────────────────────────┐
│        BACKEND DE BÚSQUEDA         │
│                                    │
│  Orquestador de consultas          │
│  Explorador de rutas               │
│  Gestión de caché                  │
│  Límites de cuota y coste          │
│  Normalización de resultados       │
└─────────────────┬──────────────────┘
                  │
          ┌───────┴────────┐
          ▼                ▼
┌─────────────────┐ ┌────────────────┐
│ APIs DE VUELOS  │ │ DATOS LOW COST │
│                 │ │                │
│ Amadeus         │ │ Fuentes        │
│ Otros proveedores│ │ autorizadas   │
│ Tarifas         │ │ Rutas/horarios │
└────────┬────────┘ └────────┬───────┘
         └─────────┬─────────┘
                   ▼
┌────────────────────────────────────┐
│       OPTIMIZADOR GARABATO         │
│                                    │
│  Precio familiar                   │
│  Tiempo adicional                  │
│  Riesgo de autoconexiones          │
│  Comparación y clasificación       │
└─────────────────┬──────────────────┘
                  ▼
┌────────────────────────────────────┐
│       RESULTADOS INTELIGENTES      │
│                                    │
│  Más barato / Mejor / Más rápido   │
│  Ahorro familiar                   │
│  Riesgos y equipaje                │
│  Enlaces externos de reserva       │
└────────────────────────────────────┘
```

**Frontend:** HTML, CSS y JavaScript, móvil primero, preparado para funcionar como PWA y alojarse en GitHub Pages si resulta viable.

**Backend:** servicio ligero y protegido para conectarse a APIs. Nunca incluir credenciales privadas en el frontend ni en un repositorio público.

**Persistencia inicial:** preferencias y favoritos almacenados localmente en el navegador. Sin cuentas de usuario ni base de datos compleja en la primera versión.

**Diseño:** componentes modulares, código organizado, interfaz visual atractiva y funcionamiento sencillo desde iPhone y ordenador.

### 7. Fuentes de datos y limitaciones

Proveedores candidatos:

**Amadeus Self-Service**
- APIs de búsqueda de ofertas y precios.
- Entorno de pruebas para validar integración.
- Cobertura incompleta, especialmente en compañías low cost.
- El entorno de pruebas no demuestra cobertura ni tarifas reales de producción.

**Travelpayouts**
- Posible fuente de precios indicativos o históricos.
- No confundir estos precios con disponibilidad actual.
- Comprobar condiciones de acceso y uso.

**Duffel**
- Posible fuente adicional.
- Su modelo de precios y relación entre búsquedas y reservas puede no ser adecuado para una aplicación familiar.
- No activar sin evaluar condiciones y costes.

**Ryanair, Wizz Air, Vueling, easyJet y otras low cost**
- Investigar fuentes de datos autorizadas.
- No asumir acceso a APIs públicas de precios.
- No depender de scraping no autorizado.
- Priorizar cobertura de rutas, horarios y tarifas cuando sea posible.

**Google Flights y Skyscanner**
- Posibles enlaces externos complementarios para comprobar y reservar.
- No asumir que proporcionan acceso libre a sus APIs.

**Pendiente de validar:** qué proveedores permiten obtener precios actuales de las low cost gratuitamente para uso familiar. Este es el principal riesgo técnico del proyecto.

### 8. Política de coste y seguridad

- Coste cero por defecto.
- No contratar servicios de pago ni activar facturación por consumo.
- Respetar límites gratuitos de las APIs.
- Utilizar caché y limitar consultas.
- No almacenar claves en archivos HTML o JavaScript públicos.
- No inventar precios ni resultados.
- Identificar claramente fuentes sin cobertura.
- No automatizar compras ni reservas.
- Redirigir al proveedor correspondiente cuando exista un enlace válido.

### 9. GitHub y despliegue — contexto histórico

El usuario ha indicado que ha activado la conexión de GitHub.

**Nombre propuesto del repositorio:** `viajeros-garabato-pedido`

Preferencia por repositorio privado. Comprobar los permisos y las condiciones de GitHub Pages antes de desplegar. No cambiar visibilidad ni publicar la aplicación sin autorización.

Estructura orientativa:

```text
viajeros-garabato-pedido/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── app.js
│   ├── search.js
│   ├── optimizer.js
│   └── airports.js
├── assets/
├── manifest.json
├── backend/
│   ├── api/
│   ├── providers/
│   └── services/
└── README.md
```

La estructura puede ajustarse durante el desarrollo para mantenerla sencilla.

### 10. Plan de desarrollo

**Fase 1 — Aplicación inicial**
- Crear el repositorio.
- Desarrollar la interfaz responsive.
- Configurar los cinco aeropuertos favoritos.
- Implementar formularios de búsqueda y fechas.
- Guardar preferencias familiares.
- Preparar la pantalla de resultados.
- No mostrar tarifas ficticias como reales.

**Fase 2 — Primera integración**
- Investigar y probar una API gratuita.
- Validar una búsqueda real con disponibilidad y precio.
- Normalizar resultados.
- Mostrar fuente, precio y fecha de consulta.

**Fase 3 — Cobertura low cost**
- Investigar fuentes autorizadas.
- Incorporar datos de rutas y horarios.
- Explorar combinaciones de vuelos independientes.
- Evaluar tiempos y riesgos de autoconexión.

**Fase 4 — Optimización**
- Implementar el algoritmo Garabato.
- Clasificar vuelos por ahorro familiar y duración.
- Mostrar comparativas y recomendaciones.
- Comparar resultados con buscadores convencionales.

**Fase 5 — Uso familiar**
- Probar desde iPhone y ordenador.
- Mejorar interfaz y rendimiento.
- Corregir errores y ampliar cobertura según nuestras búsquedas reales.

