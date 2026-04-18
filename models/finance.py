from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
import datetime
from models.base import Base

class Quota(Base):
    __tablename__ = "quotas"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    issue_date = Column(Date, default=datetime.date.today)
    due_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    quota_type = Column(String(50), default="Ordinaria") # Ordinaria, Extraordinaria
    is_paid = Column(Boolean, default=False)
    description = Column(String(200))

    unit = relationship("Unit", back_populates="quotas")
    payments = relationship("Payment", back_populates="quota")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    quota_id = Column(Integer, ForeignKey("quotas.id"), nullable=False)
    payment_date = Column(Date, default=datetime.date.today)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50)) # Transferencia, Efectivo, Cheque
    reference = Column(String(100))

    quota = relationship("Quota", back_populates="payments")

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    ruc = Column(String(20), unique=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    
    expenses = relationship("Expense", back_populates="provider")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.date.today)
    amount = Column(Float, nullable=False)
    category = Column(String(50)) # Mantenimiento, Servicios, Sueldos, etc.
    description = Column(String(255))
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    
    provider = relationship("Provider", back_populates="expenses")

class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, default=datetime.date.today)
    description = Column(String(255), nullable=False)
    status = Column(String(50), default="Pendiente") # Pendiente, En Proceso, Finalizado
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True) # Optional, can be common area
    cost = Column(Float, default=0.0)
    
    unit = relationship("Unit")
