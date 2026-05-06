from database.connection import get_session
from models.finance import Expense, Provider, Maintenance
import datetime

class OperationsController:
    def __init__(self):
        self.session = get_session()

    # --- Providers ---
    def get_all_providers(self):
        return self.session.query(Provider).all()

    def add_provider(self, ruc, name, phone, email):
        provider = Provider(ruc=ruc, name=name, phone=phone, email=email)
        self.session.add(provider)
        self.session.commit()
        return provider

    # --- Expenses ---
    def get_all_expenses(self):
        return self.session.query(Expense).all()

    def add_expense(self, amount, category, description, provider_id=None):
        expense = Expense(
            amount=amount,
            category=category,
            description=description,
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
        maint = Maintenance(
            description=description,
            unit_id=unit_id,
            status="Pendiente",
            report_date=datetime.date.today()
        )
        self.session.add(maint)
        self.session.commit()
        return maint

    def update_maintenance_status(self, maint_id, status, cost=0.0):
        maint = self.session.query(Maintenance).filter_by(id=maint_id).first()
        if not maint:
            raise ValueError("Ticket de mantenimiento no encontrado.")
        maint.status = status
        if cost > 0:
            maint.cost = cost
        self.session.commit()
        return maint
