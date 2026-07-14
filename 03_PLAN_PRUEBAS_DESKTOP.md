# Plan de Pruebas Desktop - CondoAdmin

## 1. Introducción

El presente documento constituye el Plan de Pruebas de Software para el cliente de escritorio **CondoAdmin - Cliente Desktop**, una aplicación desarrollada utilizando el lenguaje de programación Python y la biblioteca gráfica PyQt6. Esta aplicación actúa como uno de los múltiples clientes consumidores del sistema integral de administración de condominios, cuya lógica de negocio y persistencia se centralizan en una API REST construida en Spring Boot con base de datos PostgreSQL.

El objetivo primordial de este plan es definir, estructurar y organizar el proceso de validación y control de calidad de la interfaz gráfica de escritorio. Se busca garantizar que la comunicación con los servicios REST centrales sea consistente, robusta ante errores, y que se mantenga la integridad y sincronización de los datos. Cabe destacar que el cliente Desktop consume exactamente el mismo catálogo de servicios web (API REST) que los clientes Web (React) y Mobile (Flutter), por lo que se requiere asegurar el correcto envío y recepción de payloads según el contrato establecido.

---

## 2. Alcance

El esfuerzo de pruebas y validación para el cliente de escritorio se centrará exclusivamente en el núcleo funcional de administración del sistema.

### En alcance:
- **Login Administrador**: Autenticación de usuarios mediante credenciales seguras, generación del token de sesión, almacenamiento local del JWT y flujo de ingreso/denegación.
- **Gestión de Residentes (Propietarios/Inquilinos)**: Operaciones de lectura (visualización en tabla QTableWidget), creación de nuevos registros de personas, consulta/carga de detalles en formularios y edición/actualización de datos existentes a través de la interfaz.
- **Gestión de Viviendas/Unidades**: Operaciones de visualización de unidades residenciales, alta de nuevas propiedades, selección y carga de detalles, y edición/actualización de información de las unidades.

### Fuera de alcance:
- **Pagos**: Registro de alícuotas, cobranza y procesamiento de pagos en el cliente desktop.
- **Tickets**: Generación, seguimiento y flujo de órdenes de servicio o reclamos.
- **Visitas**: Registro de bitácora y autorizaciones de acceso temporal.
- **Reservas**: Gestión de áreas comunes y calendarios de uso.
- **Comunicados**: Creación y difusión de boletines informativos.
- **Otros módulos**: Cualquier funcionalidad no explícitamente detallada en el alcance de esta fase de pruebas.

---

## 3. Objetivos de las pruebas

Para asegurar el éxito de la entrega académica y la calidad de la aplicación, las pruebas perseguirán los siguientes objetivos específicos:

- **Validar el funcionamiento de la interfaz gráfica (UI PyQt6)**: Comprobar que los widgets, botones, tablas (`QTableWidget`), cuadros de diálogo (`QMessageBox`), y formularios carguen y respondan correctamente ante la interacción física (clicks, teclas, etc.).
- **Verificar la autenticación contra la API REST**: Confirmar que el flujo de login del administrador envíe correctamente la solicitud HTTP POST, gestione adecuadamente el código de respuesta (200 OK frente a 401/403) y preserve el token JWT en el cliente para solicitudes subsecuentes.
- **Comprobar el envío correcto de datos desde escritorio**: Validar que los formularios de residentes y unidades empaqueten los datos respetando los nombres y tipos requeridos por la especificación de la API (por ejemplo, validando tipos de datos enumerados, cadenas y valores numéricos como alícuotas).
- **Validar persistencia y sincronización de información**: Verificar que al realizar acciones de guardado o edición, los datos persistan correctamente en el servidor central y se refresque la visualización de manera inmediata y consistente.
- **Verificar el manejo de errores en formularios**: Garantizar que el cliente desktop valide la obligatoriedad de campos (como Número de Identidad y Nombre en Residentes o Número en Unidades) y alerte al usuario mediante ventanas emergentes controladas en caso de excepciones o respuestas erróneas del servidor.

---

## 4. Ambiente de pruebas

A continuación, se disponen los campos técnicos necesarios para registrar el entorno donde se llevarán a cabo las pruebas del cliente de escritorio:

- **Lenguaje:** Python 3
- **Framework interfaz:** PyQt6
- **Versión Python:** Python 3.8 o superior
- **Sistema operativo:** Linux
- **Base de datos utilizada:** SQLite local + PostgreSQL mediante API REST
- **URL API consumida:** https://condominio-api-2aef.onrender.com/api/v1
- **Método de ejecución del cliente:**
  ```bash
  ./run.sh
  ```
  o
  ```bash
  .venv/bin/python main.py
  ```

---

## 5. Herramientas utilizadas

- **PyAutoGUI:** Automatización de interacción con la interfaz gráfica PyQt6.
- **PyTest:** Estructuración y ejecución de casos de prueba.
- **Capturas de pantalla:** Evidencia visual de ejecución.
- **Reportes PyTest:** Registro de resultados.

---

## 6. Arquitectura evaluada

El cliente de escritorio CondoAdmin se comporta como un consumidor desacoplado del servidor central, operando sobre un modelo distribuido tradicional. El flujo de datos se esquematiza de la siguiente manera:

```
              Usuario
                 │
                 ▼
  ┌──────────────────────────────┐
  │   Aplicación Desktop PyQt6   │ (Cliente en Python)
  └──────────────┬───────────────┘
                 │
                 │ Solicitudes HTTP (JSON + JWT)
                 ▼
  ┌──────────────────────────────┐
  │     API REST Spring Boot     │ (Servidor de Aplicación Central)
  └──────────────┬───────────────┘
                 │
                 │ Consultas SQL (JDBC/JPA)
                 ▼
  ┌──────────────────────────────┐
  │   Base de Datos PostgreSQL   │ (Motor de Base de Datos Relacional)
  └──────────────────────────────┘
```

**Flujo en formato textual alternativo:**
`Usuario` ──► `Aplicación Desktop Python/PyQt6` ──► `API REST Spring Boot` ──► `Base de datos PostgreSQL`

*Nota:* El cliente de escritorio funciona como consumidor independiente de la misma API central. Utiliza clases controladoras que canalizan las solicitudes mediante un cliente HTTP interno hacia los endpoints de la API central, recibiendo objetos JSON que se deserializan para poblar de manera dinámica los componentes visuales de PyQt6.

---

## 7. Casos de prueba

La estructura de evaluación de casos de prueba funcional se define mediante la siguiente plantilla de campos:

*   **ID**: Identificador único del caso de prueba.
*   **Descripción**: Objetivo y descripción del caso evaluado.
*   **Precondiciones**: Estado inicial requerido para la ejecución de la prueba.
*   **Datos de Entrada**: Parámetros, campos de texto y datos enviados a la app.
*   **Pasos**: Secuencia detallada de acciones del operador.
*   **Resultado Esperado**: Comportamiento o mensaje esperado de la app.
*   **Resultado Obtenido**: Comportamiento real tras la ejecución (Pendiente).
*   **Estado**: Condición de la prueba (PENDIENTE/APROBADO/FALLIDO).
*   **Evidencia**: Enlace o referencia a capturas/logs de soporte (Pendiente).

---

# 7.1 Autenticación

| ID | Descripción | Precondiciones | Datos de Entrada | Pasos | Resultado Esperado | Resultado Obtenido | Estado | Evidencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DES-AUTH-001** | Login administrador correcto | Aplicación iniciada en pantalla Login. API REST disponible. Credenciales activas. | Usuario: admin<br>Contraseña: password | 1. Ejecutar aplicación.<br>2. Ubicar campo usuario.<br>3. Ingresar credenciales.<br>4. Presionar botón Ingresar. | La aplicación debe autenticar al usuario, cerrar la ventana Login y mostrar la ventana principal del sistema. | PyAutoGUI ejecutó correctamente la interacción con la interfaz. El usuario administrador ingresó correctamente y la prueba automatizada finalizó satisfactoriamente mediante PyTest. | APROBADO | Captura evidencia_login_desktop.png y reporte PyTest |
| **DES-AUTH-002** | Login con credenciales incorrectas | Aplicación iniciada en Login. API disponible. | Usuario: admin<br>Contraseña incorrecta | 1. Ejecutar aplicación.<br>2. Ingresar credenciales inválidas.<br>3. Presionar Ingresar. | El acceso debe ser rechazado y mostrar mensaje de error manteniendo la ventana Login activa. | Pendiente de ejecución | PENDIENTE | |

---

# 7.2 Residentes

| ID | Descripción | Precondiciones | Datos de Entrada | Pasos | Resultado Esperado | Resultado Obtenido | Estado | Evidencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DES-RES-001** | Visualizar lista de residentes | Administrador autenticado. API REST disponible. Residentes registrados. | Ninguno | Ejecutar aplicación, iniciar sesión y acceder a Propietarios/Inquilinos. | Mostrar lista de residentes correctamente cargada desde la API REST. | PyAutoGUI ejecutó correctamente el login y navegación hacia el módulo Residentes. | APROBADO | evidencia_visualizar_residentes_desktop.png |
| **DES-RES-002** | Crear residente | Vista Propietarios/Inquilinos disponible. API REST disponible. | Datos ingresados mediante formulario Desktop. | Completar formulario y presionar Guardar Nuevo. | Registrar residente correctamente. | PyAutoGUI completó el formulario, ejecutó el guardado y finalizó correctamente. | APROBADO | evidencia_crear_residente_desktop.png |
| **DES-RES-003** | Consultar residente | Residente existente registrado. | Selección de residente en tabla. | Acceder al módulo y seleccionar registro. | Mostrar información completa del residente. | La selección de fila cargó correctamente la información del residente en el formulario Desktop. | APROBADO | evidencia_consultar_residente_desktop.png |
| **DES-RES-004** | Actualizar residente | Residente existente cargado en formulario. | Teléfono: 0987654321<br>Dirección: Av. Nueva QA 456 | Modificar datos y presionar Actualizar. | Actualizar información correctamente mediante API REST. | PyAutoGUI realizó la modificación, ejecutó actualización y la prueba finalizó satisfactoriamente. | APROBADO | evidencia_actualizar_residente_desktop.png |

---

# 7.3 Viviendas / Unidades

| ID | Descripción | Precondiciones | Datos de Entrada | Pasos | Resultado Esperado | Resultado Obtenido | Estado | Evidencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DES-VIV-001** | Visualizar viviendas | Administrador autenticado. API REST disponible. Unidades registradas. | Ninguno | 1. Ejecutar aplicación e iniciar sesión.<br>2. Acceder al módulo "Unidades". | Mostrar lista de unidades correctamente. | PyAutoGUI ejecutó login, acceso a Unidades y carga correcta del módulo. | APROBADO | evidencia_visualizar_unidades_desktop.png |
| **DES-VIV-002** | Crear vivienda | Vista Unidades disponible. | Número: B-304, Piso: 3, Tipo: DEPARTAMENTO, Alícuota: 12.50 | 1. Completar formulario con los datos.<br>2. Presionar el botón "Guardar Nuevo".<br>3. Aceptar el mensaje de confirmación. | Crear unidad correctamente mediante API REST. | PyAutoGUI completó el formulario, ejecutó Guardar Nuevo y finalizó correctamente. | APROBADO | evidencia_crear_unidad_desktop.png |
| **DES-VIV-003** | Consultar vivienda | Unidad existente. | Selección de fila. | 1. Acceder al módulo.<br>2. Hacer clic en una fila de la tabla de unidades. | Mostrar información completa. | Selección de unidad y carga de datos ejecutada correctamente. | APROBADO | evidencia_consultar_unidad_desktop.png |
| **DES-VIV-004** | Actualizar vivienda | Unidad existente. | Modificación de alícuota. | 1. Seleccionar unidad de la tabla.<br>2. Modificar el campo Alícuota.<br>3. Presionar el botón "Actualizar".<br>4. Aceptar el mensaje de confirmación. | Actualizar información correctamente. | PyAutoGUI realizó la edición, confirmó actualización y finalizó correctamente. | APROBADO | evidencia_actualizar_unidad_desktop.png |

---

## 8. Resultados de ejecución

### Estado actual de pruebas por módulo

#### Autenticación
| Caso de Prueba | Estado |
| :--- | :--- |
| DES-AUTH-001: Login administrador correcto | ✅ APROBADO |
| DES-AUTH-002: Login con credenciales incorrectas | ⏳ PENDIENTE |

#### Residentes
| Caso de Prueba | Estado |
| :--- | :--- |
| DES-RES-001: Visualizar residentes | ✅ APROBADO |
| DES-RES-002: Crear residente | ✅ APROBADO |
| DES-RES-003: Consultar residente | ✅ APROBADO |
| DES-RES-004: Actualizar residente | ✅ APROBADO |

#### Viviendas / Unidades
| Caso de Prueba | Estado |
| :--- | :--- |
| DES-VIV-001: Visualizar viviendas | ✅ APROBADO |
| DES-VIV-002: Crear vivienda | ✅ APROBADO |
| DES-VIV-003: Consultar vivienda | ✅ APROBADO |
| DES-VIV-004: Actualizar vivienda | ✅ APROBADO |

### Resumen final Desktop

| Módulo | Casos | Resultado |
| :--- | :--- | :--- |
| Autenticación | 1 | ✅ APROBADO |
| Residentes | 4 | ✅ APROBADO |
| Viviendas | 4 | ✅ APROBADO |

### Estadística Desktop

- **Total pruebas:** 9 pruebas ejecutadas
- **Resultado:** 9 aprobadas / 0 fallidas
- **Porcentaje:** 100% éxito

---

## 9. Evidencias

- Capturas de pantalla.
- Videos de ejecución.
- Reportes PyTest.
- Logs de ejecución.

---

## 10. Incidentes encontrados

| ID | Descripción | Evidencia | Causa | Solución | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| | | | | | |

---

## 11. Conclusiones

*Espacio reservado para el análisis final de resultados de calidad del cliente de escritorio CondoAdmin, conclusiones sobre la estabilidad de la UI en PyQt6 y observaciones de la integración con la API REST central tras finalizar la ejecución física.*
