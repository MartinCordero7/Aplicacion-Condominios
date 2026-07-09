import requests
from validators import validate_cedula, validate_phone, validate_email
from controllers.auth_controller import AuthController

class MockPerson:
    def __init__(self, id, cedula, name, phone, email, tipoIdentificacion="CEDULA", fechaNacimiento="1990-01-01", direccion="", estado="ACTIVO"):
        self.id = id
        self.cedula = cedula
        self.name = name
        self.phone = phone
        self.email = email
        self.tipoIdentificacion = tipoIdentificacion
        self.fechaNacimiento = fechaNacimiento
        self.direccion = direccion
        self.estado = estado

class MockUnit:
    def __init__(self, id, identifier, unit_type, alicuota, owner_id, tenant_id, is_occupied):
        self.id = id
        self.identifier = identifier
        self.unit_type = unit_type
        self.alicuota = alicuota
        self.owner_id = owner_id
        self.tenant_id = tenant_id
        self.is_occupied = is_occupied
        # Para compatibilidad con las vistas
        self.owner = MockPerson(owner_id, "N/A", f"Propietario {owner_id}", "", "") if owner_id else None
        self.tenant = MockPerson(tenant_id, "N/A", f"Inquilino {tenant_id}", "", "") if tenant_id else None

class PropertyController:
    API_URL = "https://condominio-api-2aef.onrender.com/api/v1"

    # --- Person Methods ---
    def get_all_persons(self):
        try:
            # En el backend esto puede ser GET /residentes o /personas, asumimos /residentes
            response = requests.get(f"{self.API_URL}/residentes", headers=AuthController.get_headers(), timeout=60)
            if response.status_code == 200:
                data = response.json().get('data', {})
                content = data.get('content', data) if isinstance(data, dict) else data
                
                persons = []
                for item in content:
                    persons.append(MockPerson(
                        id=item.get('id'),
                        cedula=item.get('numeroIdentificacion', '0000000000'),
                        name=f"{item.get('nombres', '')} {item.get('apellidos', '')}".strip(),
                        phone=item.get('telefono', ''),
                        email=item.get('correo', ''),
                        tipoIdentificacion=item.get('tipoIdentificacion', 'CEDULA'),
                        fechaNacimiento=item.get('fechaNacimiento', '1990-01-01'),
                        direccion=item.get('direccion', ''),
                        estado=item.get('estado', 'ACTIVO')
                    ))
                return persons
        except Exception as e:
            print(f"Error obteniendo personas: {e}")
        return []

    def add_person(self, cedula, name, phone, email, tipoIdentificacion="CEDULA", fechaNacimiento="1990-01-01", direccion="", estado="ACTIVO"):
        cedula = cedula.strip()
        name = name.strip()
        phone = phone.strip() if phone else ""
        email = email.strip() if email else ""
        
        # Validations
        validate_cedula(cedula)
        # Assuming you'd like to disable phone/email if blank, the validators handle it.
        if phone: validate_phone(phone)
        if email: validate_email(email)
        
        parts = name.split(maxsplit=1)
        nombres = parts[0]
        apellidos = parts[1] if len(parts) > 1 else ""

        payload = {
            "tipoIdentificacion": tipoIdentificacion,
            "numeroIdentificacion": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "telefono": phone,
            "correo": email,
            "fechaNacimiento": fechaNacimiento,
            "direccion": direccion,
            "fotoPerfil": "",
            "estado": estado
        }

        response = requests.post(f"{self.API_URL}/residentes", json=payload, headers=AuthController.get_headers(), timeout=60)
        if response.status_code in [200, 201]:
            data = response.json().get('data', {})
            return MockPerson(
                id=data.get('id', 0),
                cedula=data.get('numeroIdentificacion', cedula),
                name=name,
                phone=phone,
                email=email,
                tipoIdentificacion=tipoIdentificacion,
                fechaNacimiento=fechaNacimiento,
                direccion=direccion,
                estado=estado
            )
        elif response.status_code == 400:
            error_data = response.json()
            raise Exception(f"Validación fallida: {error_data.get('message', response.text)}")
        else:
            raise Exception(f"Error API: {response.text}")

    def update_person(self, person_id, cedula, name, phone, email, tipoIdentificacion="CEDULA", fechaNacimiento="1990-01-01", direccion="", estado="ACTIVO"):
        parts = name.split(maxsplit=1)
        payload = {
            "tipoIdentificacion": tipoIdentificacion,
            "numeroIdentificacion": cedula,
            "nombres": parts[0],
            "apellidos": parts[1] if len(parts) > 1 else "",
            "telefono": phone,
            "correo": email,
            "fechaNacimiento": fechaNacimiento,
            "direccion": direccion,
            "fotoPerfil": "",
            "estado": estado
        }
        response = requests.put(f"{self.API_URL}/residentes/{person_id}", json=payload, headers=AuthController.get_headers(), timeout=60)
        if response.status_code in [200, 201]:
            return MockPerson(person_id, cedula, name, phone, email, tipoIdentificacion, fechaNacimiento, direccion, estado)
        elif response.status_code == 400:
            error_data = response.json()
            raise Exception(f"Validación fallida: {error_data.get('message', response.text)}")
        raise Exception(f"Error API: {response.text}")

    def delete_person(self, person_id):
        response = requests.delete(f"{self.API_URL}/residentes/{person_id}", headers=AuthController.get_headers(), timeout=60)
        return response.status_code in [200, 204]

    # --- Unit Methods ---
    def get_all_units(self):
        try:
            response = requests.get(f"{self.API_URL}/unidades", headers=AuthController.get_headers(), timeout=60)
            if response.status_code == 200:
                data = response.json().get('data', {})
                content = data.get('content', data) if isinstance(data, dict) else data
                
                units = []
                for item in content:
                    units.append(MockUnit(
                        id=item.get('id'),
                        identifier=item.get('numero', item.get('identifier', 'S/N')),
                        unit_type=item.get('tipo', 'DEPARTAMENTO'),
                        alicuota=item.get('alicuota', 0.0),
                        owner_id=item.get('idPropietario', None),
                        tenant_id=item.get('idInquilino', None),
                        is_occupied=item.get('ocupada', False)
                    ))
                return units
        except Exception as e:
            print(f"Error obteniendo unidades: {e}")
        return []

    def add_unit(self, identifier, unit_type, alicuota, owner_id=None, tenant_id=None):
        if alicuota < 0:
            raise ValueError("La alícuota no puede ser negativa.")
            
        payload = {
            "condominioId": 1,
            "torreId": 1,
            "estadoId": 1,
            "numero": identifier.strip(),
            "piso": "1",
            "tipo": unit_type.strip().upper(),
            "alicuota": round(float(alicuota), 4)
        }
        
        response = requests.post(f"{self.API_URL}/unidades", json=payload, headers=AuthController.get_headers(), timeout=60)
        if response.status_code in [200, 201]:
            data = response.json().get('data', {})
            return MockUnit(
                id=data.get('id', 0),
                identifier=identifier,
                unit_type=unit_type,
                alicuota=alicuota,
                owner_id=owner_id,
                tenant_id=tenant_id,
                is_occupied=(owner_id is not None or tenant_id is not None)
            )
        raise Exception(f"Error API: {response.text}")

    def update_unit(self, unit_id, identifier, unit_type, alicuota, owner_id=None, tenant_id=None):
        if alicuota < 0:
            raise ValueError("La alícuota no puede ser negativa.")
            
        payload = {
            "condominioId": 1,
            "torreId": 1,
            "estadoId": 1 if (owner_id or tenant_id) else 2,
            "numero": identifier.strip(),
            "piso": "1",
            "tipo": unit_type.strip().upper(),
            "alicuota": round(float(alicuota), 4)
        }
        
        response = requests.put(f"{self.API_URL}/unidades/{unit_id}", json=payload, headers=AuthController.get_headers(), timeout=60)
        if response.status_code in [200, 201]:
            return MockUnit(
                id=unit_id,
                identifier=identifier,
                unit_type=unit_type,
                alicuota=alicuota,
                owner_id=owner_id,
                tenant_id=tenant_id,
                is_occupied=(owner_id is not None or tenant_id is not None)
            )
        raise Exception(f"Error API: {response.text}")

    def delete_unit(self, unit_id):
        response = requests.delete(f"{self.API_URL}/unidades/{unit_id}", headers=AuthController.get_headers(), timeout=60)
        return response.status_code in [200, 204]
