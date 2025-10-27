# student_manager.py

from student_model import Student, StudentAlreadyExistsError, StudentNotFoundError, StudentError
from storage_interface import IStudentStorage  # Dependency on Storage Abstraction
from llm_interface import IQueryAgent  # Dependency on LLM Abstraction (NEW)


class StudentManager:
    """
    Core business logic class, responsible for student CRUD operations,
    data validation, and now LLM-driven query filtering.
    """

    def __init__(self, storage: IStudentStorage,
                 query_agent: IQueryAgent):  # Dependency Injection for both IStudentStorage and IQueryAgent
        self._storage = storage
        self._query_agent = query_agent  # Injected LLM Agent
        self._students = self._storage.load_data()

    # --- Validation Logic (SRP/DRY) ---
    def _validate_student_data(self, sid: str, name: str, age: int, gender: str, major: str):
        """Internal method to validate student data business rules (Centralized knowledge)."""
        if not (sid and sid.isalnum()):
            raise StudentError("ID must be non-empty alphanumeric.")
        if not (name and len(name) > 0):
            raise StudentError("Name cannot be empty.")
        if not (isinstance(age, int) and 1 <= age <= 150):
            raise StudentError("Age must be an integer between 1-150.")
        if gender not in ["Male", "Female"]:
            raise StudentError("Gender must be 'Male' or 'Female'.")
        if not (major and len(major) > 0):
            raise StudentError("Major cannot be empty.")
        return True

    def add_student(self, student: Student):
        """Adds a student. Validates data and throws an error if ID exists or data is invalid."""
        if student.sid in self._students:
            raise StudentAlreadyExistsError(student.sid)

        # Perform business rule validation
        self._validate_student_data(student.sid, student.name, student.age, student.gender, student.major)

        self._students[student.sid] = student

    def query_student_by_id(self, sid: str) -> Student:
        """Finds a student by ID. Throws an error if not found."""
        student = self._students.get(sid)
        if not student:
            raise StudentNotFoundError(sid)
        return student

    def query_students_by_name(self, name_part: str) -> list[Student]:
        """Finds students by a partial name match."""
        return [
            s for s in self._students.values()
            if name_part.lower() in s.name.lower()
        ]

    # --- NEW: LLM-driven business logic (OCP) ---
    def query_by_natural_language(self, natural_language_text: str) -> list[Student]:
        """
        Uses the LLM Agent to parse the natural language query and performs the filtering business logic.
        """
        # 1. Delegate to the LLM agent to convert natural language to structured parameters (DIP)
        query_params = self._query_agent.parse_query(natural_language_text)

        # 2. Execute parameter-based filtering logic
        results = list(self._students.values())

        # Filter based on parameters returned by the LLM
        if 'major' in query_params:
            results = [s for s in results if s.major == query_params['major']]
        if 'gender' in query_params:
            results = [s for s in results if s.gender == query_params['gender']]
        if 'age_min' in query_params:
            results = [s for s in results if s.age >= query_params['age_min']]
        if 'age_max' in query_params:
            results = [s for s in results if s.age <= query_params['age_max']]

        if 'name_part' in query_params:
            name_part = query_params['name_part'].lower()
            results = [s for s in results if name_part in s.name.lower()]

        return results

    # ----------------------------------------------

    def modify_student(self, sid: str, updates: dict):
        """Modifies a student's information, validating the new data before committing."""
        student = self.query_student_by_id(sid)

        # Store old values temporarily for validation
        temp_data = {
            'name': student.name,
            'age': student.age,
            'gender': student.gender,
            'major': student.major
        }

        # Apply updates to the temporary data
        for key, value in updates.items():
            if key in temp_data:
                temp_data[key] = value

        # Validate the combined new data
        self._validate_student_data(
            student.sid,
            temp_data['name'],
            temp_data['age'],
            temp_data['gender'],
            temp_data['major']
        )

        # Update the student object only after validation passes
        student.name = temp_data['name']
        student.age = temp_data['age']
        student.gender = temp_data['gender']
        student.major = temp_data['major']

        self._students[sid] = student

    def delete_student(self, sid: str):
        """Deletes a student. Throws an error if not found."""
        if sid not in self._students:
            raise StudentNotFoundError(sid)
        del self._students[sid]

    def get_all_students(self) -> list[Student]:
        """Gets a list of all students, sorted by ID."""
        return [self._students[sid] for sid in sorted(self._students.keys())]

    def save_and_exit(self):
        """Calls the Storage to save data."""
        self._storage.save_data(self._students)
