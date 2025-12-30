# app/models/availability.py

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime


class Availability(Base):
    __tablename__ = "availabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]

    doctor = relationship("User", back_populates="availabilities")
