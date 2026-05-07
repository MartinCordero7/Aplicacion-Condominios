from controllers.base_controller import BaseController
from models.finance import Expense, Provider, Maintenance
from validators import validate_phone, validate_email, validate_ruc
import datetime


class OperationsController(BaseController):

    # --- Providers ---
    def get_all_providers(self):
        return self.session.query(Provider).all()

    def add_provider(self, ruc, name, phone, email):
        # B-4: sanear; B-8: validar formato de RUC, teléfono y correo
        ruc   = ruc.strip()   if ruc   else ""
        name  = name.strip()
        phone = phone.strip() if phone else ""
        email = email.strip() if email else ""

        validate_ruc(ruc)
        validate_phone(phone)
        validate_email(email)

        provider = Provider(ruc=ruc, name=name, phone=phone, email=email)
        self.session.add(provider)
        self.session.commit()
        return provider

    # --- Expenses ---
    def get_all_expenses(self):
        return self.session.query(Expense).all()

    def add_expense(self, amount, category, description, provider_id=None):
        # B-1: validar que el monto sea positivo
        if amount <= 0:
            raise ValueError("El monto del egreso debe ser mayor a cero.")

        expense = Expense(
            amount=round(float(amount), 2),
            category=category.strip(),
            # B-4: sanear descripción
            description=description.strip() if description else "",
            provider_id=provider_id,
            date=datetime.date.today()
        )
        self.session.add(expense)
        self.session.commit()
        return expense

    # --- Maintenance ---
    def get_all_maintenance(self):
        return self.session.query(Maintenance).all()

    def add_maintenance(self, description, unit_id=None):
        # B-4: sanear descripción
        desc = description.strip() if description else ""
        if not desc:
            raise ValueError("La descripción del ticket no puede estar vacía.")

        maint = Maintenance(
            description=desc,
            unit_id=unit_id,
            status="Pendiente",
            report_date=datetime.date.today()
        )
        self.session.add(maint)
        self.session.commit()
        return maint

    def update_maintenance_status(self, maint_id, status, cost=0.0):
        maint = self.session.query(Maintenance).filter_by(id=maint_id).first()
        # B-7: lanzar excepción clara si no existe
        if not maint:
            raise ValueError("Ticket de mantenimiento no encontrado.")

        # B-1: validar que el costo no sea negativo
        if cost < 0:
            raise ValueError("El costo del mantenimiento no puede ser negativo.")

        maint.status = status.strip()
        if cost > 0:
            maint.cost = round(float(cost), 2)
        self.session.commit()
        return maint
