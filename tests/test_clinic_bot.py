import pytest
from datetime import datetime
import pytz
from clinic_logic import ClinicLogic

# Mock MongoDB client
class MockCollection:
    def __init__(self):
        self.data = []

    async def find(self, query):
        class MockCursor:
            async def to_list(self, length):
                return []
        return MockCursor()

    async def insert_one(self, document):
        self.data.append(document)
        return True

class MockDB:
    def __init__(self):
        self.appointments = MockCollection()

@pytest.fixture
def clinic():
    return ClinicLogic(MockDB())

@pytest.mark.asyncio
async def test_get_available_doctors(clinic):
    """Test getting available doctors"""
    today = datetime.now(pytz.UTC).strftime("%Y-%m-%d")
    available = clinic.get_available_doctors(today)
    
    # Check if all time slots are available for each doctor
    for doctor in clinic.DOCTORS:
        assert doctor in available
        assert "slots" in available[doctor]
        assert len(available[doctor]["slots"]) == len(clinic.TIMESLOTS)

@pytest.mark.asyncio
async def test_create_booking(clinic):
    """Test creating a booking"""
    test_booking = {
        "user_id": "123456",
        "doctor": "Dr. Emily Roberts",
        "date": "2025-09-10",
        "time": "09:00"
    }
    
    await clinic.create_booking(**test_booking)
    
    # Verify booking was created
    appointments = clinic.db.appointments.data
    assert len(appointments) == 1
    booking = appointments[0]
    
    assert booking["user_id"] == test_booking["user_id"]
    assert booking["doctor"] == test_booking["doctor"]
    assert booking["date"] == test_booking["date"]
    assert booking["time"] == test_booking["time"]

# ...existing code...

@pytest.mark.asyncio
async def test_invalid_doctor_booking(clinic):
    """Test booking with invalid doctor name"""
    test_booking = {
        "user_id": "123456",
        "doctor": "Dr. Invalid Name",
        "date": "2025-09-10",
        "time": "09:00"
    }
    
    with pytest.raises(ValueError, match="Invalid doctor"):
        await clinic.create_booking(**test_booking)

@pytest.mark.asyncio
async def test_invalid_timeslot_booking(clinic):
    """Test booking with invalid time slot"""
    test_booking = {
        "user_id": "123456",
        "doctor": "Dr. Emily Roberts",
        "date": "2025-09-10",
        "time": "13:00"  # Invalid time slot (lunch break)
    }
    
    with pytest.raises(ValueError, match="Invalid time slot"):
        await clinic.create_booking(**test_booking)

@pytest.mark.asyncio
async def test_double_booking_same_slot(clinic):
    """Test double booking the same time slot"""
    today = datetime.now(pytz.UTC).strftime("%Y-%m-%d")
    test_booking = {
        "user_id": "123456",
        "doctor": "Dr. Emily Roberts",
        "date": "2025-09-10",
        "time": "09:00"
    }
    
    # First booking should succeed
    await clinic.create_booking(**test_booking)
    
    # Check available slots after booking
    available = clinic.get_available_doctors(today)
    assert "09:00" not in available["Dr. Emily Roberts"]["slots"]
    assert len(available["Dr. Emily Roberts"]["slots"]) == len(clinic.TIMESLOTS) - 1

@pytest.mark.asyncio
async def test_multiple_bookings_different_doctors(clinic):
    """Test multiple bookings with different doctors"""
    bookings = [
        {
            "user_id": "123456",
            "doctor": "Dr. Emily Roberts",
            "date": "2025-09-10",
            "time": "09:00"
        },
        {
            "user_id": "789012",
            "doctor": "Dr. John Smith",
            "date": "2025-09-10",
            "time": "09:00"
        }
    ]
    
    # Create bookings
    for booking in bookings:
        await clinic.create_booking(**booking)
    
    # Verify bookings
    appointments = clinic.db.appointments.data
    assert len(appointments) == 2
    
    # Check available slots
    available = clinic.get_available_doctors(bookings[0]["date"])
    assert "09:00" not in available["Dr. Emily Roberts"]["slots"]
    assert "09:00" not in available["Dr. John Smith"]["slots"]
    assert len(available["Dr. Sarah Chen"]["slots"]) == len(clinic.TIMESLOTS)  # Still fully available