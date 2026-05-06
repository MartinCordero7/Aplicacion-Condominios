from database.connection import get_session
from models.property import Unit, Person
from models.finance import Quota, Maintenance

class PropertyController:
    def __init__(self):
        self.session = get_session()

    # --- Person Methods ---
    def get_all_persons(self):
        return self.session.query(Person).all()

    def add_person(self, cedula, name, phone, email):
        person = Person(cedula=cedula, name=name, phone=phone, email=email)
        self.session.add(person)
        self.session.commit()
        return person

    def update_person(self, person_id, cedula, name, phone, email):
        person = self.session.query(Person).filter_by(id=person_id).first()
        if person:
            person.cedula = cedula
            person.name = name
            person.phone = phone
            person.email = email
            self.session.commit()
        return person

    def delete_person(self, person_id):
        person = self.session.query(Person).filter_by(id=person_id).first()
        if person:
            if person.owned_units or person.rented_units:
                raise ValueError("No se puede eliminar la persona porque tiene unidades asociadas.")
            self.session.delete(person)
            self.session.commit()
            return True
        return False

    # --- Unit Methods ---
    def get_all_units(self):
        return self.session.query(Unit).all()

    def add_unit(self, identifier, unit_type, alicuota, owner_id=None, tenant_id=None):
        unit = Unit(
            identifier=identifier,
            unit_type=unit_type,
            alicuota=alicuota,
            owner_id=owner_id,
            tenant_id=tenant_id,
            is_occupied=tenant_id is not None or owner_id is not None
        )
        self.session.add(unit)
        self.session.commit()
        return unit

    def update_unit(self, unit_id, identifier, unit_type, alicuota, owner_id=None, tenant_id=None):
        unit = self.session.query(Unit).filter_by(id=unit_id).first()
        if unit:
            unit.identifier = identifier
            unit.unit_type = unit_type
            unit.alicuota = alicuota
            unit.owner_id = owner_id
            unit.tenant_id = tenant_id
            unit.is_occupied = tenant_id is not None or owner_id is not None
            self.session.commit()
        return unit

    def delete_unit(self, unit_id):
        unit = self.session.query(Unit).filter_by(id=unit_id).first()
        if unit:
            quotas = self.session.query(Quota).filter_by(unit_id=unit_id).first()
            maint = self.session.query(Maintenance).filter_by(unit_id=unit_id).first()
            if quotas or maint:
                raise ValueError("No se puede eliminar la unidad porque tiene cuotas o tickets de mantenimiento asociados.")
            self.session.delete(unit)
            self.session.commit()
            return True
        return False
