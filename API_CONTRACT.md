# API Contract - Sistema Condominio

**Versión:** 1.0.0  
**Fecha de actualización:** 2026-07-07  
**Autor:** Arquitectura y Desarrollo  

Este documento es la **única fuente de verdad** del sistema. Ningún cliente o servidor debe desviarse de esta estructura. 

## Matriz de Compatibilidad y Arquitectura

| Cliente | Estado |
|---------|--------|
| Spring Boot | ✅ Referencia |
| Flutter | Debe cumplir 100% |
| React | Debe cumplir 100% |
| PyQt6 | Debe cumplir 100% |

> **REGLA DE ORO:**
> Ningún cliente puede definir nombres de propiedades, tipos de datos o estructuras JSON diferentes a las especificadas en este contrato. Cualquier cambio debe realizarse primero en el `API_CONTRACT.md` y posteriormente implementarse en el backend y en todos los clientes. La API nunca se adapta al cliente, los clientes implementan el contrato.

## Convenciones Globales

- **Fechas:** Siempre formato ISO-8601 (`2026-07-07T10:00:00Z` para fecha y hora, `1990-01-01` para fechas simples).
- **Booleanos:** Valores literales `true` o `false` (nunca enteros o strings).
- **IDs:** Siempre números enteros `Long`. Ejemplo: `"id": 15` (NUNCA `"id": "15"`).
- **Enums:** Siempre en mayúsculas (ej. `ACTIVO`, `DEPARTAMENTO`, `TODOS`).
- **Nombres de atributos:** Siempre `camelCase`. Un dato se llama idénticamente igual en Request y Response (ej. `categoriaId`, `unidadId`).

## Respuestas y Errores Estándar

### Exitoso (200 OK / 201 Created)
```json
{
  "status": 200,
  "message": "Operación exitosa",
  "data": { ... },
  "errors": []
}
```

### 400 - Bad Request (Datos inválidos)
```json
{
  "status": 400,
  "message": "Datos inválidos",
  "errors": [
      {
          "campo": "correo",
          "message": "Formato inválido"
      }
  ]
}
```

### 401 - Unauthorized (Token inválido)
```json
{
   "status": 401,
   "message": "Token inválido"
}
```

### 404 - Not Found (Recurso inexistente)
```json
{
   "status": 404,
   "message": "No encontrado",
   "data": null
}
```

### 500 - Internal Server Error
```json
{
   "status": 500,
   "message": "Error interno del servidor"
}
```

---

## 1. Módulo de Autenticación (`/api/v1/auth`)

### POST - Login
**URL:** `/api/v1/auth/login`  
**Headers:** `Content-Type: application/json`

**Request JSON:**
```json
{
  "username": "admin@condominio.ec",
  "password": "password123"
}
```
**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Login exitoso",
  "data": {
    "accessToken": "eyJhb...",
    "refreshToken": "d7a8...",
    "tokenType": "Bearer",
    "expiresIn": 900000,
    "username": "admin@condominio.ec",
    "fullName": "Juan Pérez",
    "roles": ["ROLE_ADMIN"]
  }
}
```

---

## 2. Módulo de Residentes (`/api/v1/residentes`)

### GET - Listar Residentes
**URL:** `/api/v1/residentes?page=0&size=20`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Personas obtenidas",
  "data": {
    "content": [
      {
        "id": 15,
        "tipoIdentificacion": "CEDULA",
        "numeroIdentificacion": "1234567890",
        "nombres": "Juan",
        "apellidos": "Pérez",
        "telefono": "0999999999",
        "correo": "juan@example.com",
        "fechaNacimiento": "1990-01-01",
        "direccion": "Av. Principal 123",
        "fotoPerfil": "https://link.com/perfil.jpg",
        "estado": "ACTIVO"
      }
    ],
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### GET /{id} - Obtener Residente
**URL:** `/api/v1/residentes/15`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Persona encontrada",
  "data": {
    "id": 15,
    "tipoIdentificacion": "CEDULA",
    "numeroIdentificacion": "1234567890",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "telefono": "0999999999",
    "correo": "juan@example.com",
    "fechaNacimiento": "1990-01-01",
    "direccion": "Av. Principal 123",
    "fotoPerfil": "https://link.com/perfil.jpg",
    "estado": "ACTIVO"
  }
}
```

### POST - Crear Residente
**URL:** `/api/v1/residentes`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "tipoIdentificacion": "CEDULA",
  "numeroIdentificacion": "1234567890",
  "nombres": "Juan",
  "apellidos": "Pérez",
  "telefono": "0999999999",
  "correo": "juan@example.com",
  "fechaNacimiento": "1990-01-01",
  "direccion": "Av. Principal 123",
  "fotoPerfil": "https://link.com/perfil.jpg",
  "estado": "ACTIVO"
}
```
**Response JSON (201 Created):**
```json
{
  "status": 201,
  "message": "Persona creada exitosamente",
  "data": {
    "id": 16,
    "tipoIdentificacion": "CEDULA",
    "numeroIdentificacion": "1234567890",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "telefono": "0999999999",
    "correo": "juan@example.com",
    "fechaNacimiento": "1990-01-01",
    "direccion": "Av. Principal 123",
    "fotoPerfil": "https://link.com/perfil.jpg",
    "estado": "ACTIVO"
  }
}
```

### PUT /{id} - Actualizar Residente
**URL:** `/api/v1/residentes/15`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "tipoIdentificacion": "CEDULA",
  "numeroIdentificacion": "1234567890",
  "nombres": "Juan Carlos",
  "apellidos": "Pérez",
  "telefono": "0988888888",
  "correo": "juancarlos@example.com",
  "fechaNacimiento": "1990-01-01",
  "direccion": "Av. Principal 456",
  "fotoPerfil": "https://link.com/perfil_nuevo.jpg",
  "estado": "ACTIVO"
}
```
**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Persona actualizada",
  "data": {
    "id": 15,
    "tipoIdentificacion": "CEDULA",
    "numeroIdentificacion": "1234567890",
    "nombres": "Juan Carlos",
    "apellidos": "Pérez",
    "telefono": "0988888888",
    "correo": "juancarlos@example.com",
    "fechaNacimiento": "1990-01-01",
    "direccion": "Av. Principal 456",
    "fotoPerfil": "https://link.com/perfil_nuevo.jpg",
    "estado": "ACTIVO"
  }
}
```

### DELETE /{id} - Eliminar Residente
**URL:** `/api/v1/residentes/15`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (204 No Content):**  
*(Sin cuerpo, HTTP 204).*

---

## 3. Módulo de Unidades (`/api/v1/unidades`)

### GET - Listar Unidades
**URL:** `/api/v1/unidades`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Unidades obtenidas",
  "data": {
    "content": [
      {
        "id": 5,
        "condominioId": 1,
        "condominioNombre": "Las Palmas",
        "torreId": 2,
        "torreNombre": "Torre A",
        "estadoId": 1,
        "estadoNombre": "HABITADO",
        "numero": "A-101",
        "piso": "1",
        "tipo": "DEPARTAMENTO",
        "alicuota": 45.50
      }
    ],
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### GET /{id} - Obtener Unidad
**URL:** `/api/v1/unidades/5`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Unidad encontrada",
  "data": {
    "id": 5,
    "condominioId": 1,
    "condominioNombre": "Las Palmas",
    "torreId": 2,
    "torreNombre": "Torre A",
    "estadoId": 1,
    "estadoNombre": "HABITADO",
    "numero": "A-101",
    "piso": "1",
    "tipo": "DEPARTAMENTO",
    "alicuota": 45.50
  }
}
```

### POST - Crear Unidad
**URL:** `/api/v1/unidades`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "condominioId": 1,
  "torreId": 2,
  "estadoId": 1,
  "numero": "A-101",
  "piso": "1",
  "tipo": "DEPARTAMENTO",
  "alicuota": 45.50
}
```
**Response JSON (201 Created):**
```json
{
  "status": 201,
  "message": "Unidad creada exitosamente",
  "data": {
    "id": 5,
    "condominioId": 1,
    "condominioNombre": "Las Palmas",
    "torreId": 2,
    "torreNombre": "Torre A",
    "estadoId": 1,
    "estadoNombre": "HABITADO",
    "numero": "A-101",
    "piso": "1",
    "tipo": "DEPARTAMENTO",
    "alicuota": 45.50
  }
}
```

### PUT /{id} - Actualizar Unidad
**URL:** `/api/v1/unidades/5`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "condominioId": 1,
  "torreId": 2,
  "estadoId": 2,
  "numero": "A-101",
  "piso": "1",
  "tipo": "DEPARTAMENTO",
  "alicuota": 50.00
}
```
**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Unidad actualizada",
  "data": {
    "id": 5,
    "condominioId": 1,
    "condominioNombre": "Las Palmas",
    "torreId": 2,
    "torreNombre": "Torre A",
    "estadoId": 2,
    "estadoNombre": "DESHABITADO",
    "numero": "A-101",
    "piso": "1",
    "tipo": "DEPARTAMENTO",
    "alicuota": 50.00
  }
}
```

### DELETE /{id} - Eliminar Unidad
**URL:** `/api/v1/unidades/5`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (204 No Content):**  
*(Sin cuerpo, HTTP 204).*

---

## 4. Módulo de Tickets (`/api/v1/tickets`)

### GET - Listar Tickets
**URL:** `/api/v1/tickets`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Tickets obtenidos",
  "data": {
    "content": [
      {
        "id": 42,
        "personaId": 10,
        "creadoPor": "Juan Pérez",
        "unidadId": 5,
        "unidadNombre": "A-101",
        "tecnicoId": 8,
        "tecnicoNombre": "Pedro Martínez",
        "categoriaId": 2,
        "categoriaNombre": "Plomería",
        "estadoActualId": 1,
        "estado": "ABIERTO",
        "titulo": "Fuga de agua",
        "descripcion": "Problemas de fontanería",
        "prioridad": "ALTA",
        "fechaCreacion": "2026-07-07T10:00:00Z",
        "fechaCierre": null,
        "archivosUris": []
      }
    ],
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### GET /{id} - Obtener Ticket
**URL:** `/api/v1/tickets/42`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Ticket encontrado",
  "data": {
    "id": 42,
    "personaId": 10,
    "creadoPor": "Juan Pérez",
    "unidadId": 5,
    "unidadNombre": "A-101",
    "tecnicoId": 8,
    "tecnicoNombre": "Pedro Martínez",
    "categoriaId": 2,
    "categoriaNombre": "Plomería",
    "estadoActualId": 1,
    "estado": "ABIERTO",
    "titulo": "Fuga de agua",
    "descripcion": "Problemas de fontanería",
    "prioridad": "ALTA",
    "fechaCreacion": "2026-07-07T10:00:00Z",
    "fechaCierre": null,
    "archivosUris": []
  }
}
```

### POST - Crear Ticket
**URL:** `/api/v1/tickets`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "categoriaId": 2,
  "estadoActualId": 1,
  "titulo": "Fuga de agua",
  "descripcion": "Problemas de fontanería",
  "prioridad": "ALTA"
}
```
**Response JSON (201 Created):**
```json
{
  "status": 201,
  "message": "Ticket creado",
  "data": {
    "id": 42,
    "personaId": 10,
    "creadoPor": "Juan Pérez",
    "unidadId": 5,
    "unidadNombre": "A-101",
    "tecnicoId": 8,
    "tecnicoNombre": "Pedro Martínez",
    "categoriaId": 2,
    "categoriaNombre": "Plomería",
    "estadoActualId": 1,
    "estado": "ABIERTO",
    "titulo": "Fuga de agua",
    "descripcion": "Problemas de fontanería",
    "prioridad": "ALTA",
    "fechaCreacion": "2026-07-07T10:00:00Z",
    "fechaCierre": null,
    "archivosUris": []
  }
}
```

### PUT /{id} - Actualizar Ticket
**URL:** `/api/v1/tickets/42`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "categoriaId": 2,
  "estadoActualId": 2,
  "titulo": "Fuga de agua",
  "descripcion": "Problemas de fontanería solucionados",
  "prioridad": "ALTA"
}
```
**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Ticket actualizado",
  "data": {
    "id": 42,
    "personaId": 10,
    "creadoPor": "Juan Pérez",
    "unidadId": 5,
    "unidadNombre": "A-101",
    "tecnicoId": 8,
    "tecnicoNombre": "Pedro Martínez",
    "categoriaId": 2,
    "categoriaNombre": "Plomería",
    "estadoActualId": 2,
    "estado": "EN_PROGRESO",
    "titulo": "Fuga de agua",
    "descripcion": "Problemas de fontanería solucionados",
    "prioridad": "ALTA",
    "fechaCreacion": "2026-07-07T10:00:00Z",
    "fechaCierre": null,
    "archivosUris": []
  }
}
```

### DELETE /{id} - Eliminar Ticket
**URL:** `/api/v1/tickets/42`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (204 No Content):**  
*(Sin cuerpo, HTTP 204).*

---

## 5. Módulo de Visitantes (`/api/v1/visitantes`)

### GET - Listar Visitantes
**URL:** `/api/v1/visitantes`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Visitantes obtenidos",
  "data": {
    "content": [
      {
        "id": 102,
        "nombre": "Ana Sánchez",
        "cedula": "0987654321",
        "telefono": "0988888888"
      }
    ],
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### GET /{id} - Obtener Visitante
**URL:** `/api/v1/visitantes/102`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Visitante encontrado",
  "data": {
    "id": 102,
    "nombre": "Ana Sánchez",
    "cedula": "0987654321",
    "telefono": "0988888888"
  }
}
```

### POST - Crear Visitante
**URL:** `/api/v1/visitantes`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "nombre": "Ana Sánchez",
  "cedula": "0987654321",
  "telefono": "0988888888"
}
```
**Response JSON (201 Created):**
```json
{
  "status": 201,
  "message": "Visitante registrado exitosamente",
  "data": {
    "id": 102,
    "nombre": "Ana Sánchez",
    "cedula": "0987654321",
    "telefono": "0988888888"
  }
}
```

### PUT /{id} - Actualizar Visitante
**URL:** `/api/v1/visitantes/102`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "nombre": "Ana Sánchez",
  "cedula": "0987654321",
  "telefono": "0999999999"
}
```
**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Visitante actualizado",
  "data": {
    "id": 102,
    "nombre": "Ana Sánchez",
    "cedula": "0987654321",
    "telefono": "0999999999"
  }
}
```

### DELETE /{id} - Eliminar Visitante
**URL:** `/api/v1/visitantes/102`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (204 No Content):**  
*(Sin cuerpo, HTTP 204).*

---

## 6. Módulo de Comunicados (`/api/v1/comunicados`)

### GET - Listar Comunicados
**URL:** `/api/v1/comunicados`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Comunicados obtenidos",
  "data": {
    "content": [
      {
        "id": 10,
        "titulo": "Corte de agua",
        "mensaje": "Habrá corte de agua por mantenimiento preventivo.",
        "fecha": "2026-07-07T10:00:00Z",
        "autorId": 1,
        "autorNombres": "Administrador",
        "autorApellidos": "Principal",
        "destinatarioTipo": "TODOS",
        "destinatarioId": null
      }
    ],
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### GET /{id} - Obtener Comunicado
**URL:** `/api/v1/comunicados/10`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Comunicado encontrado",
  "data": {
    "id": 10,
    "titulo": "Corte de agua",
    "mensaje": "Habrá corte de agua por mantenimiento preventivo.",
    "fecha": "2026-07-07T10:00:00Z",
    "autorId": 1,
    "autorNombres": "Administrador",
    "autorApellidos": "Principal",
    "destinatarioTipo": "TODOS",
    "destinatarioId": null
  }
}
```

### POST - Crear Comunicado
**URL:** `/api/v1/comunicados`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "titulo": "Corte de agua",
  "mensaje": "Habrá corte de agua por mantenimiento preventivo.",
  "autorId": 1,
  "destinatarioTipo": "TODOS",
  "destinatarioId": null
}
```
**Response JSON (201 Created):**
```json
{
  "status": 201,
  "message": "Comunicado creado",
  "data": {
    "id": 10,
    "titulo": "Corte de agua",
    "mensaje": "Habrá corte de agua por mantenimiento preventivo.",
    "fecha": "2026-07-07T10:00:00Z",
    "autorId": 1,
    "autorNombres": "Administrador",
    "autorApellidos": "Principal",
    "destinatarioTipo": "TODOS",
    "destinatarioId": null
  }
}
```

### PUT /{id} - Actualizar Comunicado
**URL:** `/api/v1/comunicados/10`  
**Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>`

**Request JSON:**
```json
{
  "titulo": "Corte de agua (Actualizado)",
  "mensaje": "El corte de agua será desde las 14:00 hasta las 18:00.",
  "autorId": 1,
  "destinatarioTipo": "TODOS",
  "destinatarioId": null
}
```
**Response JSON (200 OK):**
```json
{
  "status": 200,
  "message": "Comunicado actualizado",
  "data": {
    "id": 10,
    "titulo": "Corte de agua (Actualizado)",
    "mensaje": "El corte de agua será desde las 14:00 hasta las 18:00.",
    "fecha": "2026-07-07T10:00:00Z",
    "autorId": 1,
    "autorNombres": "Administrador",
    "autorApellidos": "Principal",
    "destinatarioTipo": "TODOS",
    "destinatarioId": null
  }
}
```

### DELETE /{id} - Eliminar Comunicado
**URL:** `/api/v1/comunicados/10`  
**Headers:** `Authorization: Bearer <token>`

**Response JSON (204 No Content):**  
*(Sin cuerpo, HTTP 204).*
