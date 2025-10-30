# cli_interface.py

import sys
from student_model import Student, StudentError, StudentNotFoundError
from student_manager import StudentManager
from student_storage import StudentStorage  # Needed for main's concrete instantiation
from storage_interface import IStudentStorage  # Needed for main's type hint
# New LLM related imports
from llm_interface import IQueryAgent
from llm_query_agent import LLMQueryAgent


class CLIInterface:
    """Command Line Interface class, responsible for user interaction (Presentation Layer)."""

    def __init__(self, manager: StudentManager):
        self._manager = manager

    # --- Helper Methods: Refactored (KISS/Refactoring) ---

    def _prompt_for_student_data(self, current_student: Student = None) -> dict:
        """
        Uses 'Extract Method' refactoring.
        Collects all student inputs for add and modify operations.
        It delegates business validation to the Manager.
        """
        data = {}

        if current_student:
            print("Enter new information (press enter to keep unchanged):")

            # Modification
            data['name'] = input(f"New Name ({current_student.name}): ").strip() or current_student.name
            age_str = input(f"New Age ({current_student.age}): ").strip()
            # Handle empty input and type conversion
            data['age'] = int(age_str) if age_str.isdigit() else current_student.age

            data['gender'] = input(f"New Gender ({current_student.gender}): ").strip() or current_student.gender
            data['major'] = input(f"New Major ({current_student.major}): ").strip() or current_student.major

            data['sid'] = current_student.sid

        else:
            # Creation
            data['sid'] = input("Enter Student ID (e.g., S101): ").strip()
            data['name'] = input("Enter Name: ").strip()
            age_str = input("Enter Age (integer): ").strip()
            # Handle type conversion
            data['age'] = int(age_str) if age_str.isdigit() else 0  # Will be caught by manager validation

            data['gender'] = input("Enter Gender (Male/Female): ").strip()
            data['major'] = input("Enter Major: ").strip()

        return data

    # --- CLI Actions ---

    def add_student(self):
        """Action: Add a student."""
        print("\n--- Add Student ---")
        try:
            data = self._prompt_for_student_data()
            self._manager.add_student(
                sid=data['sid'],
                name=data['name'],
                age=data['age'],
                gender=data['gender'],
                major=data['major']
            )
            print(f"Student {data['sid']} added successfully!")
        except StudentError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def query_student(self):
        """Action: Query students using natural language."""
        print("\n--- Query Student (Natural Language) ---")
        query = input("Enter query (e.g., 'all females over 20'): ").strip()

        try:
            results = self._manager.query_by_llm(query)

            print("\nQuery Results:")
            if not results:
                print("No students matched the query criteria.")
            else:
                for student in results:
                    print(student)

        except StudentError as e:
            print(f"Query Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def modify_student(self):
        """Action: Modify an existing student."""
        print("\n--- Modify Student ---")
        sid = input("Enter Student ID to modify: ").strip()

        try:
            current_student = self._manager.get_student(sid)
            print("Current data:")
            print(current_student)

            data = self._prompt_for_student_data(current_student)

            # Use current student's attributes if not updated in prompt_for_student_data
            self._manager.update_student(
                sid=sid,
                name=data.get('name', current_student.name),
                age=data.get('age', current_student.age),
                gender=data.get('gender', current_student.gender),
                major=data.get('major', current_student.major)
            )
            print("Modification successful.")

        except StudentNotFoundError as e:
            print(f"Error: {e}")
        except StudentError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def delete_student(self):
        """Action: Delete a student."""
        print("\n--- Delete Student ---")
        sid = input("Enter Student ID to delete: ").strip()
        try:
            self._manager.delete_student(sid)
            print(f"Student {sid} deleted successfully.")
        except StudentNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def show_all(self):
        """Action: Show all students."""
        print("\n--- All Students ---")
        students = self._manager.get_all_students()
        if not students:
            print("No students in the system.")
        else:
            for student in students:
                print(student)

    def save_and_exit(self):
        """Action: Save data and exit the program."""
        print("\nSaving data and exiting...")
        try:
            self._manager.save_data()
            print("Data saved. Goodbye!")
        except Exception as e:
            print(f"Data save failed during exit: {e}")
        sys.exit(0)


def main():
    """Program entry point: Instantiates objects and runs the CLI (Dependency Injection)."""

    # 1. Instantiate Storage (Concrete implementation of IStudentStorage)
    storage: IStudentStorage = StudentStorage()

    # 2. Instantiate LLM Agent (Concrete implementation of IQueryAgent)
    query_agent: IQueryAgent = LLMQueryAgent()

    # 3. Instantiate Manager, injecting both dependencies
    manager = StudentManager(storage, query_agent)

    # 4. Instantiate CLI Interface
    cli = CLIInterface(manager)

    menu_actions = {
        "1": cli.add_student,
        "2": cli.query_student,
        "3": cli.modify_student,
        "4": cli.delete_student,
        "5": cli.show_all,
        "6": cli.save_and_exit,
    }

    while True:
        print("\n" + "=" * 30)
        print("        Student Management System        ")
        print("=" * 30)
        print("1. Add Student")
        print("2. Query Student (with Natural Language)")
        print("3. Modify Student")
        print("4. Delete Student")
        print("5. Show All")
        print("6. Save and Exit")
        print("=" * 30)

        choice = input("Select operation (1-6): ").strip()
        action = menu_actions.get(choice)

        if action:
            action()
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
