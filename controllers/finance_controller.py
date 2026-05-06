from database.connection import get_session
from models.finance import Quota, Payment
from models.property import Unit
import datetime

class FinanceController:
    def __init__(self):
        self.session = get_session()

    # --- Quotas Methods ---
    def get_all_quotas(self):
        return self.session.query(Quota).all()

    def generate_monthly_quotas(self, amount_per_alicuota, due_date):
        desc = f"Cuota Mensual {datetime.date.today().strftime('%Y-%m')}"
        existing = self.session.query(Quota).filter_by(description=desc).first()
        if existing:
            raise ValueError("Las cuotas mensuales ya fueron generadas para este mes.")
        
        units = self.session.query(Unit).all()
        generated = 0
        for unit in units:
            if unit.alicuota > 0:
                amount = amount_per_alicuota * unit.alicuota
                quota = Quota(
                    unit_id=unit.id,
                    due_date=due_date,
                    amount=amount,
                    quota_type="Ordinaria",
                    description=desc
                )
                self.session.add(quota)
                generated += 1
        self.session.commit()
        return generated

    def add_quota(self, unit_id, due_date, amount, quota_type, description):
        quota = Quota(
            unit_id=unit_id,
            due_date=due_date,
            amount=amount,
            quota_type=quota_type,
            description=description
        )
        self.session.add(quota)
        self.session.commit()
        return quota

    def pay_quota(self, quota_id, amount_paid, payment_method, reference):
        quota = self.session.query(Quota).filter_by(id=quota_id).first()
        if not quota:
            raise ValueError("Cuota no encontrada.")
        if quota.is_paid:
            raise ValueError("La cuota ya ha sido pagada.")
        
        payment = Payment(
            quota_id=quota.id,
            amount_paid=amount_paid,
            payment_method=payment_method,
            reference=reference
        )
        quota.is_paid = True 
        self.session.add(payment)
        self.session.commit()
        return payment
