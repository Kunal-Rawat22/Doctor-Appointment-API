from pydantic import BaseModel
from datetime import datetime
from .userSchema import UserResponseDTO

class AppointmentResponseDTO(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    start_time: datetime
    end_time: datetime
    patient: UserResponseDTO
    doctor: UserResponseDTO
    class Config:
        from_attributes = True

class AppointmentRequestCO(BaseModel):
    doctor_id: int
    patient_id: int
    start_time: datetime
    end_time: datetime
    availability_id: int