import requests
import datetime
from controllers.base_controller import BaseController
from models.finance import Expense, Provider, Maintenance
from validators import validate_phone, validate_email, validate_ruc
from controllers.auth_controller import AuthController

class MockMaintenance:
    def __init__(self, id, description, unit_id, status, report_date, cost):
        self.id = id
        self.description = description
        self.unit_id = unit_id
        self.status = status
        self.report_date = report_date
        self.cost = cost

class OperationsController(BaseController):
    API_URL = "https://condominio-api-2aef.onrender.com/api/v1"

    # --- Providers (Almacenados en SQLite local) ---
    def get_all_providers(self):
        return self.session.query(Provider).all()

    def add_provider(self, ruc, name, phone, email, address="", service_type=""):
        ruc   = ruc.strip()   if ruc   else ""
        name  = name.strip()
        phone = phone.strip() if phone else ""
        email = email.strip() if email else ""
        address = address.strip() if address else ""
        service_type = service_type.strip() if service_type else ""

        validate_ruc(ruc)
        validate_phone(phone)
        validate_email(email)

        provider = Provider(ruc=ruc, name=name, phone=phone, email=email, address=address, service_type=service_type)
        self.session.add(provider)
        self.session.commit()
        return provider

    # --- Expenses (Almacenados en SQLite y como Tickets en Spring Boot) ---
    def get_all_expenses(self):
        return self.session.query(Expense).all()

    def add_expense(self, amount, category, description, provider_id=None):
        if amount <= 0:
            raise ValueError("El monto del egreso debe ser mayor a cero.")
        if not provider_id:
            raise ValueError("No puede existir un gasto sin asignar un proveedor previamente registrado.")

        provider = self.session.query(Provider).filter_by(id=provider_id).first()
        if not provider:
            raise ValueError("El proveedor seleccionado no existe.")

        # 1. Crear el Ticket en el Backend (Spring Boot)
        desc_completa = f"Proveedor: {provider.name}\nMonto: ${amount}\nFecha: {datetime.date.today()}\nCategoría: {category}\nObservaciones: {description}"
        
        payload = {
            "categoriaId": 3,
            "estadoActualId": 1,
            "titulo": f"Mantenimiento - {category}",
            "descripcion": desc_completa,
            "prioridad": "ALTA"
        }
        
        response = requests.post(f"{self.API_URL}/tickets", json=payload, headers=AuthController.get_headers(), timeout=60)
        if response.status_code not in [200, 201]:
            raise Exception(f"No se pudo crear el Ticket en la API: HTTP {response.status_code} - {response.text}")

        # 2. Guardar el Expense en SQLite local (para reportes y la tabla de la UI)
        expense = Expense(
            amount=round(float(amount), 2),
            category=category.strip(),
            description=description.strip() if description else "",
            provider_id=provider_id,
            date=datetime.date.today()
        )
        self.session.add(expense)
        self.session.commit()
        return expense

    # --- Maintenance (Mapeado a Tickets API) ---
    def get_all_maintenance(self):
        try:
            response = requests.get(f"{self.API_URL}/tickets", headers=AuthController.get_headers(), timeout=60)
            if response.status_code == 200:
                data = response.json().get('data', {})
                content = data.get('content', data) if isinstance(data, dict) else data

                maint_list = []
                for item in content:
                    maint_list.append(MockMaintenance(
                        id=item.get('id'),
                        description=item.get('titulo', '') + " - " + item.get('descripcion', ''),
                        unit_id=item.get('unidadId'),
                        status=item.get('estado', 'ABIERTO'),  # ABIERTO|EN_PROGRESO|CERRADO|CANCELADO
                        report_date=item.get('fechaCreacion', ''),
                        cost=0.0
                    ))
                return maint_list
        except Exception as e:
            print(f"Error obteniendo tickets de mantenimiento: {e}")
        return []

    def add_maintenance(self, description, unit_id=None):
        desc = description.strip() if description else ""
        if not desc:
            raise ValueError("La descripción del ticket no puede estar vacía.")

        payload = {
            "categoriaId": 2,
            "estadoActualId": 1,
            "titulo": desc[:50],
            "descripcion": desc,
            "prioridad": "MEDIA"
        }
        
        response = requests.post(f"{self.API_URL}/tickets", json=payload, headers=AuthController.get_headers(), timeout=60)
        if response.status_code in [200, 201]:
            data = response.json().get('data', {})
            return MockMaintenance(
                id=data.get('id', 0),
                description=description,
                unit_id=unit_id,
                status=data.get('estado', "ABIERTO"),
                report_date=data.get('fechaCreacion', str(datetime.date.today())),
                cost=0.0
            )
        raise Exception(f"Error API: {response.text}")

    def update_maintenance_status(self, maint_id, estado_id, cost=0.0):
        """Actualiza el estado de un ticket. estado_id es el FK a estado_ticket (int)."""
        if cost < 0:
            raise ValueError("El costo del mantenimiento no puede ser negativo.")

        try:
            # Primero obtenemos los datos actuales del ticket para hacer un PUT completo
            response_get = requests.get(f"{self.API_URL}/tickets/{maint_id}", headers=AuthController.get_headers(), timeout=60)
            if response_get.status_code == 200:
                ticket_data = response_get.json().get('data', {})
                payload = {
                    "categoriaId": ticket_data.get('categoriaId', 1),
                    "estadoActualId": int(estado_id),
                    "titulo": ticket_data.get('titulo', 'Mantenimiento'),
                    "descripcion": ticket_data.get('descripcion', 'Actualizado desde Desktop'),
                    "prioridad": ticket_data.get('prioridad', 'MEDIA')
                }
                response = requests.put(
                    f"{self.API_URL}/tickets/{maint_id}",
                    json=payload,
                    headers=AuthController.get_headers(),
                    timeout=60
                )
            else:
                raise Exception(f"No se pudo obtener el ticket: HTTP {response_get.status_code}")

            if response.status_code in [200, 201]:
                data = response.json().get('data', {})
                return MockMaintenance(
                    id=maint_id,
                    description="Actualizado",
                    unit_id=None,
                    status=data.get('estado', 'EN_PROGRESO'),
                    report_date=str(datetime.date.today()),
                    cost=cost
                )
            raise Exception(f"Error API: {response.text}")
        except requests.exceptions.RequestException as e:
             raise Exception(f"Error de conexión: {e}")
