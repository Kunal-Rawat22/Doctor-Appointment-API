from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from .enums import UserRole

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)

    availabilities = relationship("Availability", back_populates="doctor", cascade="all, delete-orphan")

    appointments_as_patient = relationship(
        "Appointment",
        back_populates="patient",
        foreign_keys="Appointment.patient_id",
        cascade="all, delete-orphan"
    )

    appointments_as_doctor = relationship(
        "Appointment",
        back_populates="doctor",
        foreign_keys="Appointment.doctor_id",
        cascade="all, delete-orphan"
    )

