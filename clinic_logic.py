from datetime import datetime
from typing import Dict, List

class ClinicLogic:
    def __init__(self, db):
        self.db = db
        self.DOCTORS = {
            "Dr. Emily Roberts": "General Veterinarian",
            "Dr. John Smith": "Surgery Specialist",
            "Dr. Sarah Chen": "Pet Dentistry"
        }
        self.TIMESLOTS = [
            "09:00", "10:00", "11:00", "12:00", 
            "14:00", "15:00", "16:00", "17:00"
        ]

    def get_available_doctors(self, date: str) -> Dict:
       """Get available doctors and their free time slots for a specific date"""
       try:
           bookings = self.db.appointments.data
       except Exception as e:
           print(f"Error fetching bookings: {e}")
           bookings = []  # Default to empty list if error occurs

       # Create set of booked slots
       booked_slots = {(b['doctor'], b['time']) for b in bookings}
    
       # Initialize available doctors dictionary
       available_doctors = {}
       for doc, spec in self.DOCTORS.items():
           free_slots = []
           for time in self.TIMESLOTS:
               if (doc, time) not in booked_slots:
                   free_slots.append(time)
           if free_slots:  # Only include doctors with available slots
               available_doctors[doc] = {"specialty": spec, "slots": free_slots}
       return available_doctors

    async def create_booking(self, user_id: str, doctor: str, date: str, time: str):
        """Create a booking and remove the time slot from availability"""
        if doctor not in self.DOCTORS:
            raise ValueError("Invalid doctor")
        if time not in self.TIMESLOTS:
            raise ValueError("Invalid time slot")
            
        # Check if slot is already booked
        try:
            existing = self.db.appointments.find({
                "doctor": doctor,
                "date": date,
                "time": time
            }).to_list(None)
        except Exception as e:
            print(f"Error checking existing bookings: {e}")
            existing = []
        if existing:
            raise ValueError(f"Time slot {time} is already booked for {doctor}")
        
        booking = {
            "user_id": user_id,
            "doctor": doctor,
            "date": date,
            "time": time,
            "created_at": datetime.utcnow()
        }
        # Insert the booking and update available slots
        try:
            await self.db.appointments.insert_one(booking)
            return booking
        except Exception as e:
            raise ValueError(f"Failed to create booking: {str(e)}")