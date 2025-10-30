# storage_interface.py

from abc import ABC, abstractmethod
from student_model import Student


class IStudentStorage(ABC):
    """
    Dependency Inversion Principle (DIP):
    Defines the storage abstraction (Abstraction).
    StudentManager will depend on this interface, not the concrete implementation.
    """

    @abstractmethod
    def load_data(self) -> dict[str, Student]:
        """Loads student data from persistent storage."""
        pass

    @abstractmethod
    def save_data(self, students: dict[str, Student]):
        """Saves student data to persistent storage."""
        pass
