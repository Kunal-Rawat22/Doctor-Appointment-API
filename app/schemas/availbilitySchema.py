from pydantic import BaseModel
from datetime import datetime

class AvailabilitySetRequestCO(BaseModel):
    doctor_id: int
    start_time: datetime
    end_time: datetime
    max_appointments: int

class AvailabilityResponseDTO(BaseModel):
    doctor_id: int
    start_time: datetime
    end_time: datetime
    booked_appointments: int
    max_appointments: int