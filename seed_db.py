import datetime
from database.connection import get_session, init_db
from models.user import User
from models.property import Person, Unit
from models.finance import Quota, Payment, Provider, Expense, Maintenance
import hashlib

def seed():
    session = get_session()
    
    # Check if we already seeded
    if session.query(Person).count() >= 5:
        print("La base de datos ya contiene registros de prueba.")
        return

    # 1. Insert 5 Users
    for i in range(1, 6):
        hashed_pw = hashlib.sha256("pass123".encode()).hexdigest()
        user = User(username=f"user{i}", password_hash=hashed_pw, full_name=f"Usuario Operativo {i}", role="Operativo")
        session.add(user)

    # 2. Insert 5 Persons (Propietarios/Inquilinos)
    persons = []
    for i in range(1, 6):
        person = Person(
            cedula=f"170000000{i}", 
            name=f"Propietario {i}", 
            phone=f"099000000{i}", 
            email=f"prop{i}@mail.com"
        )
        session.add(person)
        persons.append(person)
    
    session.commit()

    # 3. Insert 5 Units
    units = []
    for i in range(1, 6):
        unit = Unit(
            identifier=f"Dpto 10{i}",
            unit_type="Departamento",
            alicuota=2.5 + i,
            owner_id=persons[i-1].id,
            is_occupied=True
        )
        session.add(unit)
        units.append(unit)
        
    session.commit()

    # 4. Insert 5 Quotas
    quotas = []
    for i in range(1, 6):
        quota = Quota(
            unit_id=units[i-1].id,
            issue_date=datetime.date.today() - datetime.timedelta(days=i*10),
            due_date=datetime.date.today() + datetime.timedelta(days=15),
            amount=50.0 + (i * 10),
            quota_type="Ordinaria",
            description=f"Cuota ordinaria Dpto 10{i}"
        )
        session.add(quota)
        quotas.append(quota)
        
    session.commit()

    # 5. Insert 5 Payments
    for i in range(1, 6):
        payment = Payment(
            quota_id=quotas[i-1].id,
            payment_date=datetime.date.today(),
            amount_paid=quotas[i-1].amount,
            payment_method="Transferencia",
            reference=f"REF-00{i}"
        )
        quotas[i-1].is_paid = True
        session.add(payment)

    # 6. Insert 5 Providers
    providers = []
    for i in range(1, 6):
        provider = Provider(
            ruc=f"179000000{i}001",
            name=f"Empresa Servicios {i} S.A.",
            phone=f"02200000{i}",
            email=f"contacto@empresa{i}.com"
        )
        session.add(provider)
        providers.append(provider)
        
    session.commit()

    # 7. Insert 5 Expenses
    for i in range(1, 6):
        expense = Expense(
            date=datetime.date.today() - datetime.timedelta(days=i),
            amount=100.0 * i,
            category="Mantenimiento",
            description=f"Reparación general {i}",
            provider_id=providers[i-1].id
        )
        session.add(expense)

    # 8. Insert 5 Maintenance Tickets
    for i in range(1, 6):
        maint = Maintenance(
            report_date=datetime.date.today() - datetime.timedelta(days=i),
            description=f"Foco quemado en pasillo {i}",
            status="Pendiente",
            unit_id=None,
            cost=0.0
        )
        session.add(maint)

    session.commit()
    print("Base de datos poblada con 5 registros por tabla exitosamente.")

if __name__ == "__main__":
    init_db()
    seed()
