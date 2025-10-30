# student_storage.py

import os
import pickle
from student_model import Student
from storage_interface import IStudentStorage # Import the abstract interface

class StudentStorage(IStudentStorage): # Implements the interface
    """
    Independent data persistence class, responsible for disk I/O.
    This is a Concrete class that implements the IStudentStorage interface.
    It uses pickle for serialization.
    """
    def __init__(self, data_file="students.data"):
        self.data_file = data_file

    def load_data(self) -> dict[str, Student]:
        """Loads student data from file (Implements interface method)"""
        students = {}
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "rb") as f:
                    students = pickle.load(f)
                print(f"[{self.__class__.__name__}] Data loaded successfully from {self.data_file}!")
            except Exception as e:
                print(f"[{self.__class__.__name__}] Data loading failed: {e}")
        else:
            print(f"[{self.__class__.__name__}] No historical data, returning empty dictionary.")
        return students

    def save_data(self, students: dict[str, Student]):
        """Saves student data to file (Implements interface method)"""
        try:
            with open(self.data_file, "wb") as f:
                pickle.dump(students, f)
            print(f"[{self.__class__.__name__}] Data saved successfully to {self.data_file}!")
        except Exception as e:
            print(f"[{self.__class__.__name__}] Data saving failed: {e}")
