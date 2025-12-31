import pytest
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt

from app.service import user_service
from app.schemas import userSchema
from app.models.enums import UserRole
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.config import settings


class TestUserRegistration:
    """Test suite for user registration functionality."""
    
    @pytest.mark.asyncio
    async def test_register_doctor_success(self, db_session):
        """Test successful doctor registration."""
        user_data = userSchema.UserRequestCO(
            name="Dr. Test Doctor",
            email="newdoctor@test.com",
            password="securepassword123",
            role="DOCTOR"
        )
        
        result = await user_service.create_user(db_session, user_data)
        
        assert result is not None
        assert result.email == "newdoctor@test.com"
        assert result.name == "Dr. Test Doctor"
        assert result.role == UserRole.DOCTOR
        assert result.hashed_password != "securepassword123"  # Should be hashed
        assert verify_password("securepassword123", result.hashed_password)
    
    @pytest.mark.asyncio
    async def test_register_patient_success(self, db_session):
        """Test successful patient registration."""
        user_data = userSchema.UserRequestCO(
            name="Test Patient",
            email="newpatient@test.com",
            password="securepassword123",
            role="PATIENT"
        )
        
        result = await user_service.create_user(db_session, user_data)
        
        assert result is not None
        assert result.email == "newpatient@test.com"
        assert result.name == "Test Patient"
        assert result.role == UserRole.PATIENT
        assert verify_password("securepassword123", result.hashed_password)
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db_session, sample_doctor):
        """Test registration with duplicate email fails."""
        user_data = userSchema.UserRequestCO(
            name="Another Doctor",
            email=sample_doctor.email,  # Using existing email
            password="password123",
            role="DOCTOR"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(db_session, user_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_register_invalid_role(self, db_session):
        """Test registration with invalid role fails."""
        user_data = userSchema.UserRequestCO(
            name="Test User",
            email="invalid@test.com",
            password="password123",
            role="INVALID_ROLE"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(db_session, user_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid Role" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_register_password_hashing(self, db_session):
        """Test that passwords are properly hashed."""
        user_data = userSchema.UserRequestCO(
            name="Test User",
            email="hash@test.com",
            password="plaintextpassword",
            role="PATIENT"
        )
        
        result = await user_service.create_user(db_session, user_data)
        
        # Password should be hashed, not plain text
        assert result.hashed_password != "plaintextpassword"
        assert len(result.hashed_password) > 50  # Bcrypt hashes are long
        # Should be able to verify the original password
        assert verify_password("plaintextpassword", result.hashed_password)
        # Wrong password should fail
        assert not verify_password("wrongpassword", result.hashed_password)


class TestUserLogin:
    """Test suite for user login functionality."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, db_session, sample_doctor):
        """Test successful login returns JWT token."""
        login_request = userSchema.UserLoginRequestCO(
            username=sample_doctor.email,
            password="password123"
        )
        
        result = await user_service.login_user(db_session, login_request)
        
        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert len(result["access_token"]) > 0
        
        # Verify token can be decoded
        decoded = decode_token(result["access_token"])
        assert decoded["sub"] == sample_doctor.email
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, db_session):
        """Test login with non-existent email fails."""
        login_request = userSchema.UserLoginRequestCO(
            username="nonexistent@test.com",
            password="password123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await user_service.login_user(db_session, login_request)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, db_session, sample_doctor):
        """Test login with wrong password fails."""
        login_request = userSchema.UserLoginRequestCO(
            username=sample_doctor.email,
            password="wrongpassword"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await user_service.login_user(db_session, login_request)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_login_patient_success(self, db_session, sample_patient):
        """Test patient can login successfully."""
        login_request = userSchema.UserLoginRequestCO(
            username=sample_patient.email,
            password="password123"
        )
        
        result = await user_service.login_user(db_session, login_request)
        
        assert "access_token" in result
        decoded = decode_token(result["access_token"])
        assert decoded["sub"] == sample_patient.email


class TestPasswordSecurity:
    """Test suite for password hashing and verification."""
    
    def test_hash_password(self):
        """Test password hashing produces different hashes."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Same password should produce different hashes (due to salt)
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_password_strength(self):
        """Test that hashed passwords are secure."""
        password = "simple"
        hashed = hash_password(password)
        
        # Bcrypt hashes should be at least 60 characters
        assert len(hashed) >= 60
        # Should not contain the original password
        assert password not in hashed


class TestJWTToken:
    """Test suite for JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com", "role": "doctor"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_access_token(self):
        """Test JWT token decoding."""
        data = {"sub": "test@example.com", "role": "doctor"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded  # Expiry should be added
    
    def test_token_expiry(self):
        """Test that tokens have expiry time."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert "exp" in decoded
        # Expiry should be in the future
        assert decoded["exp"] > datetime.now().timestamp()
    
    def test_token_invalid_signature(self):
        """Test that tokens with invalid signature fail to decode."""
        # Create a token with wrong secret
        from jose import jwt as jose_jwt
        invalid_token = jose_jwt.encode(
            {"sub": "test@example.com"},
            "wrong-secret-key",
            algorithm="HS256"
        )
        
        with pytest.raises(Exception):  # JWTError
            decode_token(invalid_token)


class TestForgetPassword:
    """Test suite for password reset functionality."""
    
    @pytest.mark.asyncio
    async def test_forget_password_success(self, db_session, sample_doctor):
        """Test successful password reset."""
        old_password_hash = sample_doctor.hashed_password
        
        request = userSchema.UserForgetPasswordCO(
            email=sample_doctor.email,
            new_password="newpassword123",
            otp="123456"
        )
        
        result = await user_service.forget_password(db_session, request)
        
        assert result["message"] == "Password Updated Successfully"
        
        # Verify password was changed
        await db_session.refresh(sample_doctor)
        assert sample_doctor.hashed_password != old_password_hash
        assert verify_password("newpassword123", sample_doctor.hashed_password)
    
    @pytest.mark.asyncio
    async def test_forget_password_user_not_found(self, db_session):
        """Test password reset with non-existent user fails."""
        request = userSchema.UserForgetPasswordCO(
            email="nonexistent@test.com",
            new_password="newpassword123",
            otp="123456"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await user_service.forget_password(db_session, request)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_forget_password_invalid_otp(self, db_session, sample_doctor):
        """Test password reset with invalid OTP fails."""
        request = userSchema.UserForgetPasswordCO(
            email=sample_doctor.email,
            new_password="newpassword123",
            otp="wrongotp"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await user_service.forget_password(db_session, request)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid OTP" in exc_info.value.detail


class TestRoleValidation:
    """Test suite for role-based validation."""
    
    @pytest.mark.asyncio
    async def test_doctor_role_uppercase(self, db_session):
        """Test that DOCTOR role (uppercase) is accepted."""
        user_data = userSchema.UserRequestCO(
            name="Dr. Test",
            email="doctor_upper@test.com",
            password="password123",
            role="DOCTOR"
        )
        
        result = await user_service.create_user(db_session, user_data)
        assert result.role == UserRole.DOCTOR
    
    @pytest.mark.asyncio
    async def test_patient_role_uppercase(self, db_session):
        """Test that PATIENT role (uppercase) is accepted."""
        user_data = userSchema.UserRequestCO(
            name="Test Patient",
            email="patient_upper@test.com",
            password="password123",
            role="PATIENT"
        )
        
        result = await user_service.create_user(db_session, user_data)
        assert result.role == UserRole.PATIENT
    
    @pytest.mark.asyncio
    async def test_case_sensitive_role_validation(self, db_session):
        """Test that role validation is case-sensitive."""
        # Lowercase should fail based on the service logic
        user_data = userSchema.UserRequestCO(
            name="Test User",
            email="lowercase@test.com",
            password="password123",
            role="doctor"  # lowercase
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(db_session, user_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
