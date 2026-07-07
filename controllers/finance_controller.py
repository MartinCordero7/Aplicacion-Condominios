import requests
import datetime
from models.property import Unit
from controllers.property_controller import PropertyController

class MockQuota:
    def __init__(self, id, unit_id, due_date, amount, quota_type, description, is_paid, issue_date=None):
        self.id = id
        self.unit_id = unit_id
        self.due_date = due_date
        self.amount = amount
        self.quota_type = quota_type
        self.description = description
        self.is_paid = is_paid
        self.issue_date = issue_date or str(datetime.date.today())

class MockPayment:
    def __init__(self, id, quota_id, amount_paid, payment_method, reference):
        self.id = id
        self.quota_id = quota_id
        self.amount_paid = amount_paid
        self.payment_method = payment_method
        self.reference = reference

class FinanceController:
    API_URL = "https://condominio-api-2aef.onrender.com/api/v1"

    def get_all_quotas(self):
        try:
            # Endpoint /cuotas no es oficial en API_CONTRACT.md. Eliminado por auditoría.
            print("Endpoint /cuotas eliminado por no estar en el contrato oficial.")
            return []
        except Exception as e:
            print(f"Error obteniendo cuotas: {e}")
        return []

    def generate_monthly_quotas(self, amount_per_alicuota, due_date):
        if amount_per_alicuota <= 0:
            raise ValueError("El monto base por alícuota debe ser mayor a cero.")
            
        desc = f"Cuota Mensual {datetime.date.today().strftime('%Y-%m')}"
        
        # En una arquitectura real, esto debería ser un endpoint del backend (ej. POST /cuotas/generar-mes)
        # Aquí lo simulamos trayendo las unidades y creando cuotas una a una
        property_controller = PropertyController()
        units = property_controller.get_all_units()
        
        generated = 0
        for unit in units:
            if unit.alicuota > 0:
                amount = amount_per_alicuota * unit.alicuota
                self.add_quota(unit.id, due_date.isoformat() if hasattr(due_date, 'isoformat') else str(due_date), amount, "ORDINARIA", desc)
                generated += 1
                
        return generated

    def add_quota(self, unit_id, due_date, amount, quota_type, description):
        if amount <= 0:
            raise ValueError("El monto de la cuota debe ser mayor a cero.")
            
        payload = {
            "idUnidad": unit_id,
            "tipo": quota_type.strip().upper(),
            "monto": round(float(amount), 2),
            "mes": datetime.date.today().month,
            "anio": datetime.date.today().year,
            "fechaVencimiento": due_date.isoformat() if hasattr(due_date, 'isoformat') else str(due_date)
        }
        
        # Endpoint /cuotas POST no es oficial. Eliminado por auditoría.
        print("Creación de cuota omitida: Endpoint /cuotas no oficial.")
        return MockQuota(
            id=0,
            unit_id=unit_id,
            due_date=due_date,
            amount=amount,
            quota_type=quota_type,
            description=description,
            is_paid=False
        )

    def pay_quota(self, quota_id, amount_paid, payment_method, reference):
        payload = {
            "idCuota": quota_id,
            "montoPagado": round(float(amount_paid), 2),
            "metodoPago": payment_method.strip().upper(),
            "referencia": reference.strip() if reference else "",
            "fechaPago": datetime.date.today().isoformat()
        }
        
        # Endpoint /pagos POST no es oficial. Eliminado por auditoría.
        print("Registro de pago omitido: Endpoint /pagos no oficial.")
        return MockPayment(
            id=0,
            quota_id=quota_id,
            amount_paid=amount_paid,
            payment_method=payment_method,
            reference=reference
        )

