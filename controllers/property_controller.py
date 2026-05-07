from controllers.base_controller import BaseController
from models.property import Unit, Person
from models.finance import Quota, Maintenance
from validators import validate_cedula, validate_phone, validate_email


class PropertyController(BaseController):

    # --- Person Methods ---
    def get_all_persons(self):
        return self.session.query(Person).all()

    def add_person(self, cedula, name, phone, email):
        # B-4: sanear; B-8: validar formato
        cedula = cedula.strip()
        name = name.strip()
        phone = phone.strip() if phone else ""
        email = email.strip() if email else ""

        validate_cedula(cedula)
        validate_phone(phone)
        validate_email(email)

        person = Person(cedula=cedula, name=name, phone=phone, email=email)
        self.session.add(person)
        self.session.commit()
        return person

    def update_person(self, person_id, cedula, name, phone, email):
        # B-4: sanear; B-8: validar formato
        cedula = cedula.strip()
        name = name.strip()
        phone = phone.strip() if phone else ""
        email = email.strip() if email else ""

        validate_cedula(cedula)
        validate_phone(phone)
        validate_email(email)

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
            # B-3: verificar integridad referencial antes de eliminar
            if person.owned_units or person.rented_units:
                raise ValueError(
                    "No se puede eliminar la persona porque tiene unidades asociadas. "
                    "Desasóciela de todas sus unidades primero."
                )
            self.session.delete(person)
            self.session.commit()
            return True
        return False

    # --- Unit Methods ---
    def get_all_units(self):
        return self.session.query(Unit).all()

    def add_unit(self, identifier, unit_type, alicuota, owner_id=None, tenant_id=None):
        # B-1: validar que la alícuota no sea negativa
        if alicuota < 0:
            raise ValueError("La alícuota no puede ser negativa.")

        unit = Unit(
            # B-4: sanear identificador
            identifier=identifier.strip(),
            unit_type=unit_type.strip(),
            alicuota=round(float(alicuota), 4),
            owner_id=owner_id,
            tenant_id=tenant_id,
            is_occupied=tenant_id is not None or owner_id is not None
        )
        self.session.add(unit)
        self.session.commit()
        return unit

    def update_unit(self, unit_id, identifier, unit_type, alicuota, owner_id=None, tenant_id=None):
        # B-1: validar que la alícuota no sea negativa
        if alicuota < 0:
            raise ValueError("La alícuota no puede ser negativa.")

        unit = self.session.query(Unit).filter_by(id=unit_id).first()
        if unit:
            unit.identifier = identifier.strip()
            unit.unit_type = unit_type.strip()
            unit.alicuota = round(float(alicuota), 4)
            unit.owner_id = owner_id
            unit.tenant_id = tenant_id
            unit.is_occupied = tenant_id is not None or owner_id is not None
            self.session.commit()
        return unit

    def delete_unit(self, unit_id):
        unit = self.session.query(Unit).filter_by(id=unit_id).first()
        if unit:
            # B-3: verificar integridad referencial — cuotas y tickets de mantenimiento
            quotas = self.session.query(Quota).filter_by(unit_id=unit_id).first()
            maint = self.session.query(Maintenance).filter_by(unit_id=unit_id).first()
            if quotas:
                raise ValueError(
                    "No se puede eliminar la unidad porque tiene cuotas asociadas. "
                    "Elimine primero todas sus cuotas."
                )
            if maint:
                raise ValueError(
                    "No se puede eliminar la unidad porque tiene tickets de mantenimiento asociados. "
                    "Cierre o elimine los tickets primero."
                )
            self.session.delete(unit)
            self.session.commit()
            return True
        return False
