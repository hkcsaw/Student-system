# Student-system
    def delete_student(self):
        """Delete student"""
        print("\n----- Delete Student -----")
        if not self.students:
            print("No student information available!")
            return

        sid = input("Enter student ID to delete: ").strip()
        student = self.students.get(sid)
        if not student:
            print(f"No student found with ID {sid}!")
            return

        confirm = input(f"Are you sure to delete student {student.name} (ID: {sid})? (y/n): ").strip().lower()
        if confirm == "y":
            del self.students[sid]
            print(f"Student {student.name} deleted successfully!")
        else:
            print("Deletion canceled")
