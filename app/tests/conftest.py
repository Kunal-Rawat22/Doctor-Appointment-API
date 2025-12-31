import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.core.database import Base, get_db
from app.models.user import User
from app.models.Appointment import Appointment
from app.models.Availability import Availability
from app.models.enums import UserRole
from app.core.security import hash_password
from app.core.config import Settings

# Test database URL (using SQLite in-memory for faster tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db(db_session):
    """Dependency override for get_db."""
    async def override_get_db():
        yield db_session
    return override_get_db


@pytest.fixture
def test_settings():
    """Test settings with test secret key."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        secret_key="test-secret-key-for-testing-only",
        algorithm="HS256",
        access_token_expire_minutes=30
    )


@pytest.fixture
async def sample_doctor(db_session):
    """Create a sample doctor user."""
    doctor = User(
        name="Dr. John Doe",
        email="doctor@test.com",
        hashed_password=hash_password("password123"),
        role=UserRole.DOCTOR
    )
    db_session.add(doctor)
    await db_session.commit()
    await db_session.refresh(doctor)
    return doctor


@pytest.fixture
async def sample_patient(db_session):
    """Create a sample patient user."""
    patient = User(
        name="Jane Patient",
        email="patient@test.com",
        hashed_password=hash_password("password123"),
        role=UserRole.PATIENT
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture
async def sample_availability(db_session, sample_doctor):
    """Create a sample availability for the doctor."""
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=8)
    
    availability = Availability(
        doctor_id=sample_doctor.id,
        start_time=start_time,
        end_time=end_time,
        max_appointments=5,
        booked_appointments=0
    )
    db_session.add(availability)
    await db_session.commit()
    await db_session.refresh(availability)
    return availability


@pytest.fixture
async def sample_appointment(db_session, sample_doctor, sample_patient, sample_availability):
    """Create a sample appointment."""
    start_time = sample_availability.start_time + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        doctor_id=sample_doctor.id,
        patient_id=sample_patient.id,
        start_time=start_time,
        end_time=end_time,
        availability_id=sample_availability.id,
        deleted=False
    )
    db_session.add(appointment)
    sample_availability.booked_appointments = 1
    await db_session.commit()
    await db_session.refresh(appointment)
    return appointment

