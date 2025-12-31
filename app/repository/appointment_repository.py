from sqlalchemy.ext.asyncio import AsyncSession
from app.models.Appointment import Appointment
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime

async def fetch_by_doctor_id_and_patient_id_and_availability_id(doctor_id: int, patient_id: int, availability_id: int, db: AsyncSession):
    query = (
            select(Appointment)
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.patient_id == patient_id,
                    Appointment.availability_id == availability_id
                )
            )
        )

    result = await db.execute(query)
    return result.scalars().first()

async def save_appointment(db: AsyncSession, appointment: Appointment):
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    result = await db.execute(
        select(Appointment)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.doctor)
        )
        .where(Appointment.id == appointment.id)
    )

    return result.scalars().first()

async def fetch_all_doctor_upcoming_appointments(doctor_id:int, limit:int, offset:int, current_time: datetime, db: AsyncSession):
    query = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor)
            )
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.start_time >= current_time,
                    Appointment.deleted == False
                )
            )
            .order_by(Appointment.id)
            .offset(offset)
            .limit(limit)
        )
    result = await db.execute(query)
    return result.scalars().all()

async def fetch_all_patient_upcoming_appointments(patient_id:int, limit:int, offset:int, current_time: datetime, db: AsyncSession):
    query = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor)
            )
            .where(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.start_time >= current_time,
                    Appointment.deleted == False
                )
            )
            .order_by(Appointment.id)
            .offset(offset)
            .limit(limit)
        )
    result = await db.execute(query)
    return result.scalars().all()

async def fetch_by_patient_id_and_appointment_id(patient_id:int, appointment_id:int, db: AsyncSession):
    query = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor)
            )
            .where(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.id == appointment_id,
                    Appointment.deleted == False
                )
            )
        )
    result = await db.execute(query)
    return result.scalars().first()

async def update_appointment(db: AsyncSession, appointment: Appointment):
    await db.commit()
    await db.refresh(appointment)
    return appointment