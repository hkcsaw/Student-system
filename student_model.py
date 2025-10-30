
# student_model.py

from dataclasses import dataclass

@dataclass
class Student:
    """Defines the Student data model using dataclass."""
    sid: str
    name: str
    age: int
    gender: str  # Male/Female
    major: str

    def __str__(self):
        """Formatted output of student information."""
        return f"ID: {self.sid}\tName: {self.name}\tAge: {self.age}\tGender: {self.gender}\tMajor: {self.major}"

# --- Business Exceptions ---
class StudentError(Exception):
    """Base exception for the Student Management System."""
    pass

class StudentAlreadyExistsError(StudentError):
    """Raised when trying to add a student whose ID already exists."""
    def __init__(self, sid):
        super().__init__(f"Student ID {sid} already exists.")

class StudentNotFoundError(StudentError):
    """Raised when querying/modifying/deleting a non-existent student."""
    def __init__(self, sid):
        super().__init__(f"No student found with ID {sid}.")
