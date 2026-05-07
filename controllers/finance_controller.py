from controllers.base_controller import BaseController
from models.finance import Quota, Payment
from models.property import Unit
import datetime


class FinanceController(BaseController):

    # --- Quotas Methods ---
    def get_all_quotas(self):
        return self.session.query(Quota).all()

    def generate_monthly_quotas(self, amount_per_alicuota, due_date):
        # B-1: validar que el monto base sea positivo
        if amount_per_alicuota <= 0:
            raise ValueError("El monto base por alícuota debe ser mayor a cero.")

        desc = f"Cuota Mensual {datetime.date.today().strftime('%Y-%m')}"

        # B-6: impedir doble generación para el mismo mes
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
        # B-1: validar monto positivo
        if amount <= 0:
            raise ValueError("El monto de la cuota debe ser mayor a cero.")

        quota = Quota(
            unit_id=unit_id,
            due_date=due_date,
            amount=round(float(amount), 2),
            quota_type=quota_type,
            # B-4: sanear cadenas de texto
            description=description.strip() if description else ""
        )
        self.session.add(quota)
        self.session.commit()
        return quota

    def pay_quota(self, quota_id, amount_paid, payment_method, reference):
        quota = self.session.query(Quota).filter_by(id=quota_id).first()
        # B-7: lanzar excepción clara si la cuota no existe
        if not quota:
            raise ValueError("Cuota no encontrada.")
        # B-2: impedir pagos duplicados
        if quota.is_paid:
            raise ValueError("Esta cuota ya ha sido pagada anteriormente.")

        payment = Payment(
            quota_id=quota.id,
            amount_paid=round(float(amount_paid), 2),
            # B-4: sanear cadenas
            payment_method=payment_method.strip(),
            reference=reference.strip() if reference else ""
        )
        quota.is_paid = True
        self.session.add(payment)
        self.session.commit()
        return payment
