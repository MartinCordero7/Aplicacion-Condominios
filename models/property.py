from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import Base

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    
    # Relationships
    owned_units = relationship("Unit", back_populates="owner", foreign_keys='Unit.owner_id')
    rented_units = relationship("Unit", back_populates="tenant", foreign_keys='Unit.tenant_id')

class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(20), unique=True, index=True, nullable=False) # e.g. "Apt 101"
    unit_type = Column(String(50)) # e.g. "Departamento", "Casa", "Local"
    alicuota = Column(Float, default=0.0) # Percentage of participation
    is_occupied = Column(Boolean, default=False)
    
    owner_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("persons.id"), nullable=True)

    owner = relationship("Person", foreign_keys=[owner_id], back_populates="owned_units")
    tenant = relationship("Person", foreign_keys=[tenant_id], back_populates="rented_units")
    
    quotas = relationship("Quota", back_populates="unit")
