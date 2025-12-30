# app/models/appointment.py

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    patient = relationship(
        "User",
        back_populates="appointments_as_patient",
        foreign_keys=[patient_id]
    )
    doctor = relationship(
        "User",
        back_populates="appointments_as_doctor",
        foreign_keys=[doctor_id]
    )
