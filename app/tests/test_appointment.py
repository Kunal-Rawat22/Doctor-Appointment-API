import pytest
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.service import appointment_service
from app.schemas import appointmentSchema
from app.models.enums import UserRole
 

class TestCreateAppointment:
    """Test suite for appointment creation functionality."""
    
    @pytest.mark.asyncio
    async def test_create_appointment_success(
        self, db_session, sample_doctor, sample_patient, sample_availability
    ):
        """Test successful appointment creation."""
        start_time = sample_availability.start_time + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        request = appointmentSchema.AppointmentRequestCO(
            doctor_id=sample_doctor.id,
            patient_id=sample_patient.id,
            start_time=start_time,
            end_time=end_time,
            availability_id=sample_availability.id
        )
        
        result = await appointment_service.create_appointment(request, db_session)
        
        assert result is not None
        assert result.doctor_id == sample_doctor.id
        assert result.patient_id == sample_patient.id
        assert result.availability_id == sample_availability.id
        assert result.deleted is False
        
        # Verify availability booked_appointments increased
        await db_session.refresh(sample_availability)
        assert sample_availability.booked_appointments == 1
    
    @pytest.mark.asyncio
    async def test_create_appointment_doctor_not_found(
        self, db_session, sample_patient, sample_availability
    ):
        """Test appointment creation with non-existent doctor fails."""
        start_time = sample_availability.start_time + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        request = appointmentSchema.AppointmentRequestCO(
            doctor_id=99999,  # Non-existent doctor
            patient_id=sample_patient.id,
            start_time=start_time,
            end_time=end_time,
            availability_id=sample_availability.id
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.create_appointment(request, db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Doctor not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_create_appointment_patient_not_found(
        self, db_session, sample_doctor, sample_availability
    ):
        """Test appointment creation with non-existent patient fails."""
        start_time = sample_availability.start_time + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        request = appointmentSchema.AppointmentRequestCO(
            doctor_id=sample_doctor.id,
            patient_id=99999,  # Non-existent patient
            start_time=start_time,
            end_time=end_time,
            availability_id=sample_availability.id
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.create_appointment(request, db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Patient not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_create_appointment_duplicate_booking(
        self, db_session, sample_doctor, sample_patient, 
        sample_availability, sample_appointment
    ):
        """Test that duplicate booking fails."""
        start_time = sample_availability.start_time + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        request = appointmentSchema.AppointmentRequestCO(
            doctor_id=sample_doctor.id,
            patient_id=sample_patient.id,
            start_time=start_time,
            end_time=end_time,
            availability_id=sample_availability.id
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.create_appointment(request, db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Already booked" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_create_appointment_availability_not_found(
        self, db_session, sample_doctor, sample_patient
    ):
        """Test appointment creation with non-existent availability fails."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        request = appointmentSchema.AppointmentRequestCO(
            doctor_id=sample_doctor.id,
            patient_id=sample_patient.id,
            start_time=start_time,
            end_time=end_time,
            availability_id=99999  # Non-existent availability
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.create_appointment(request, db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Availibility not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_create_appointment_timing_outside_availability(
        self, db_session, sample_doctor, sample_patient, sample_availability
    ):
        """Test appointment timing outside availability range fails."""
        # Start before availability starts
        start_time = sample_availability.start_time - timedelta(hours=1)
        end_time = sample_availability.end_time + timedelta(hours=1)
        
        request = appointmentSchema.AppointmentRequestCO(
            doctor_id=sample_doctor.id,
            patient_id=sample_patient.id,
            start_time=start_time,
            end_time=end_time,
            availability_id=sample_availability.id
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.create_appointment(request, db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Appointment timing not within" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_create_appointment_availability_full(
        self, db_session, sample_doctor, sample_patient, sample_availability
    ):
        """Test appointment creation when availability is full fails."""
        # Fill up the availability
        sample_availability.max_appointments = 2
        sample_availability.booked_appointments = 2
        await db_session.commit()
        
        start_time = sample_availability.start_time + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        request = appointmentSchema.AppointmentRequestCO(
            doctor_id=sample_doctor.id,
            patient_id=sample_patient.id,
            start_time=start_time,
            end_time=end_time,
            availability_id=sample_availability.id
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.create_appointment(request, db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "exceeded max appointments" in exc_info.value.detail


class TestCancelAppointment:
    """Test suite for appointment cancellation functionality."""
    
    @pytest.mark.asyncio
    async def test_cancel_appointment_success(
        self, db_session, sample_patient, sample_appointment, sample_availability
    ):
        """Test successful appointment cancellation."""
        initial_booked = sample_availability.booked_appointments
        
        result = await appointment_service.cancel_apppointment(
            sample_appointment.id,
            sample_patient.id,
            db_session
        )
        
        assert result["message"] == "Appointment cancelled Successfully"
        
        # Verify appointment is marked as deleted
        await db_session.refresh(sample_appointment)
        assert sample_appointment.deleted is True
        
        # Verify availability booked_appointments decreased
        await db_session.refresh(sample_availability)
        assert sample_availability.booked_appointments == initial_booked - 1
    
    @pytest.mark.asyncio
    async def test_cancel_appointment_not_found(
        self, db_session, sample_patient
    ):
        """Test cancellation of non-existent appointment fails."""
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.cancel_apppointment(
                99999,  # Non-existent appointment
                sample_patient.id,
                db_session
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Appointment doesn't exist" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_cancel_appointment_wrong_patient(
        self, db_session, sample_doctor, sample_appointment
    ):
        """Test that a patient cannot cancel another patient's appointment."""
        # Try to cancel with wrong patient ID
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.cancel_apppointment(
                sample_appointment.id,
                99999,  # Wrong patient ID
                db_session
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Appointment doesn't exist" in exc_info.value.detail


class TestFetchAppointments:
    """Test suite for fetching appointments."""
    
    @pytest.mark.asyncio
    async def test_fetch_doctor_upcoming_appointments(
        self, db_session, sample_doctor, sample_appointment
    ):
        """Test fetching doctor's upcoming appointments."""
        result = await appointment_service.fetch_all_doctor_upcoming_appointments(
            sample_doctor.id,
            limit=10,
            offset=0,
            db=db_session
        )
        
        assert isinstance(result, list)
        assert len(result) >= 1
        # Verify appointment is in results
        appointment_ids = [apt.id for apt in result]
        assert sample_appointment.id in appointment_ids
    
    @pytest.mark.asyncio
    async def test_fetch_doctor_appointments_pagination(
        self, db_session, sample_doctor, sample_appointment
    ):
        """Test pagination for doctor appointments."""
        # First page
        result_page1 = await appointment_service.fetch_all_doctor_upcoming_appointments(
            sample_doctor.id,
            limit=1,
            offset=0,
            db=db_session
        )
        
        # Second page
        result_page2 = await appointment_service.fetch_all_doctor_upcoming_appointments(
            sample_doctor.id,
            limit=1,
            offset=1,
            db=db_session
        )
        
        assert len(result_page1) <= 1
        assert len(result_page2) <= 1
        # Results should be different (if there are multiple appointments)
        if len(result_page1) > 0 and len(result_page2) > 0:
            assert result_page1[0].id != result_page2[0].id
    
    @pytest.mark.asyncio
    async def test_fetch_patient_upcoming_appointments(
        self, db_session, sample_patient, sample_appointment
    ):
        """Test fetching patient's upcoming appointments."""
        result = await appointment_service.fetch_all_patient_upcoming_appointments(
            sample_patient.id,
            limit=10,
            offset=0,
            db=db_session
        )
        
        assert isinstance(result, list)
        assert len(result) >= 1
        # Verify appointment is in results
        appointment_ids = [apt.id for apt in result]
        assert sample_appointment.id in appointment_ids
    
    @pytest.mark.asyncio
    async def test_fetch_patient_appointments_pagination(
        self, db_session, sample_patient, sample_appointment
    ):
        """Test pagination for patient appointments."""
        result_page1 = await appointment_service.fetch_all_patient_upcoming_appointments(
            sample_patient.id,
            limit=1,
            offset=0,
            db=db_session
        )
        
        result_page2 = await appointment_service.fetch_all_patient_upcoming_appointments(
            sample_patient.id,
            limit=1,
            offset=1,
            db=db_session
        )
        
        assert len(result_page1) <= 1
        assert len(result_page2) <= 1
    
    @pytest.mark.asyncio
    async def test_fetch_appointments_excludes_deleted(
        self, db_session, sample_doctor, sample_appointment
    ):
        """Test that deleted appointments are not returned."""
        # Cancel the appointment
        await appointment_service.cancel_apppointment(
            sample_appointment.id,
            sample_appointment.patient_id,
            db_session
        )
        
        # Fetch appointments - deleted one should not appear
        result = await appointment_service.fetch_all_doctor_upcoming_appointments(
            sample_doctor.id,
            limit=10,
            offset=0,
            db=db_session
        )
        
        appointment_ids = [apt.id for apt in result]
        assert sample_appointment.id not in appointment_ids
    
    @pytest.mark.asyncio
    async def test_fetch_appointments_only_upcoming(
        self, db_session, sample_doctor, sample_patient, sample_availability
    ):
        """Test that only upcoming appointments are returned."""
        from app.models.Appointment import Appointment
        
        # Create a past appointment
        past_start = datetime.now() - timedelta(days=1)
        past_end = past_start + timedelta(hours=1)
        
        past_appointment = Appointment(
            doctor_id=sample_doctor.id,
            patient_id=sample_patient.id,
            start_time=past_start,
            end_time=past_end,
            availability_id=sample_availability.id,
            deleted=False
        )
        db_session.add(past_appointment)
        await db_session.commit()
        
        # Fetch upcoming appointments
        result = await appointment_service.fetch_all_doctor_upcoming_appointments(
            sample_doctor.id,
            limit=10,
            offset=0,
            db=db_session
        )
        
        # Past appointment should not be in results
        appointment_ids = [apt.id for apt in result]
        assert past_appointment.id not in appointment_ids


class TestAppointmentValidations:
    """Test suite for appointment validation logic."""
    
    @pytest.mark.asyncio
    async def test_verify_doctor_and_patient_valid(
        self, db_session, sample_doctor, sample_patient
    ):
        """Test verification of valid doctor and patient."""
        # Should not raise exception
        await appointment_service.verify_doctor_and_patient(
            db_session,
            sample_doctor.id,
            sample_patient.id
        )
    
    @pytest.mark.asyncio
    async def test_verify_doctor_and_patient_invalid_doctor(
        self, db_session, sample_patient
    ):
        """Test verification fails with invalid doctor."""
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.verify_doctor_and_patient(
                db_session,
                99999,  # Invalid doctor
                sample_patient.id
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Doctor not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_verify_doctor_and_patient_invalid_patient(
        self, db_session, sample_doctor
    ):
        """Test verification fails with invalid patient."""
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.verify_doctor_and_patient(
                db_session,
                sample_doctor.id,
                99999  # Invalid patient
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Patient not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_verify_duplicate_booking_none_exists(
        self, db_session, sample_doctor, sample_patient, sample_availability
    ):
        """Test duplicate booking check when no booking exists."""
        # Should not raise exception
        await appointment_service.verify_duplicate_booking(
            db_session,
            sample_doctor.id,
            sample_patient.id,
            sample_availability.id
        )
    
    @pytest.mark.asyncio
    async def test_verify_duplicate_booking_exists(
        self, db_session, sample_doctor, sample_patient, 
        sample_availability, sample_appointment
    ):
        """Test duplicate booking check when booking exists."""
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.verify_duplicate_booking(
                db_session,
                sample_doctor.id,
                sample_patient.id,
                sample_availability.id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Already booked" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_verify_availability_consistent_booking(
        self, db_session, sample_availability
    ):
        """Test availability verification with consistent booking."""
        start_time = sample_availability.start_time + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        # Should not raise exception
        result = await appointment_service.verify_consistent_booking_with_availability(
            db_session,
            end_time,
            start_time,
            sample_availability.id
        )
        
        assert result is not None
        assert result.id == sample_availability.id
    
    @pytest.mark.asyncio
    async def test_verify_availability_inconsistent_timing(
        self, db_session, sample_availability
    ):
        """Test availability verification with inconsistent timing."""
        # Appointment outside availability range
        start_time = sample_availability.start_time - timedelta(hours=1)
        end_time = sample_availability.end_time + timedelta(hours=1)
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.verify_consistent_booking_with_availability(
                db_session,
                end_time,
                start_time,
                sample_availability.id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Appointment timing not within" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_verify_availability_max_appointments_reached(
        self, db_session, sample_availability
    ):
        """Test availability verification when max appointments reached."""
        # Set availability to full
        sample_availability.max_appointments = 2
        sample_availability.booked_appointments = 2
        await db_session.commit()
        
        start_time = sample_availability.start_time + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(HTTPException) as exc_info:
            await appointment_service.verify_consistent_booking_with_availability(
                db_session,
                end_time,
                start_time,
                sample_availability.id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "exceeded max appointments" in exc_info.value.detail

