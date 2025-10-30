# main_api.py
# The final stable version: Includes Jinja2 UI rendering, fixed Type Error, and added a Web UI manual save data API.
# [Fix: AttributeError: 'StudentManager' object has no attribute 'query_students_by_llm']

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Query, Request
from fastapi.templating import Jinja2Templates  # Import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # Import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import webbrowser
import threading
import time

# --- Import core components of the existing project ---
try:
    from student_model import Student, StudentError, StudentNotFoundError, StudentAlreadyExistsError
    from student_manager import StudentManager
    from student_storage import StudentStorage
    from llm_query_agent import LLMQueryAgent
    from storage_interface import IStudentStorage
    from llm_interface import IQueryAgent
except ImportError as e:
    print(f"Fatal Error: Failed to import core modules. Please ensure all files exist. Error: {e}")
    sys.exit(1)


# -----------------------------------------------------------

# --- 1. Pydantic Models for API Data Validation and Serialization (Pydantic V2 compatible) ---

class StudentBase(BaseModel):
    """Base fields for student data."""
    name: str = Field(..., max_length=50)
    age: int = Field(..., gt=0, le=150)
    gender: str = Field(..., pattern="^(Male|Female)$")
    major: str = Field(..., max_length=50)

class StudentUpdate(StudentBase):
    """Model for student update. All fields are optional."""
    name: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, gt=0, le=150)
    gender: Optional[str] = Field(None, pattern="^(Male|Female)$")
    major: Optional[str] = Field(None, max_length=50)

class StudentCreate(StudentBase):
    """Model for student creation. Inherits from StudentBase, allowing for an optional sid."""
    sid: Optional[str] = Field(None, description="Optional Student ID. If not provided, a UUID will be generated.")

class LLMQueryResponse(BaseModel):
    """Model for the LLM-driven query response."""
    students: List[Student]
    query_params: Dict[str, Any]

# -----------------------------------------------------------

# --- 2. Application Setup and Dependency Injection ---

# Instantiate concrete dependencies
storage_implementation: IStudentStorage = StudentStorage()
query_agent_implementation: IQueryAgent = LLMQueryAgent()

# Dependency Injection: Manager is instantiated with concrete Storage and LLM Agent.
manager = StudentManager(storage_implementation, query_agent_implementation)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create a lifespan context manager to load/save data automatically on startup/shutdown.
    print("Application startup: Loading student data...")
    # Data is loaded in StudentManager.__init__

    yield  # Application runs

    print("Application shutdown: Saving student data...")
    try:
        manager.save_data()
    except Exception as e:
        print(f"Error during shutdown data save: {e}")


app = FastAPI(
    title="Student Management System API (FastAPI + LLM Agent)",
    description="A demonstration of a layered architecture with FastAPI, Dependency Injection, and an LLM-driven query feature.",
    version="1.0.0",
    lifespan=lifespan # Attach the lifespan context manager
)

# Templates configuration (Jinja2 Templates for Web UI)
templates = Jinja2Templates(directory="templates")

# Static files configuration (for assets like images, CSS, JS, audio)
app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------------------------------------

# --- 3. API Endpoints (Controller/Presentation Layer) ---

@app.get("/students/{sid}", response_model=Student, summary="1. Get Student Detail by ID")
def get_student_detail_api(sid: str):
    """Retrieves a single student's details by their Student ID (sid)."""
    try:
        return manager.get_student(sid)
    except StudentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StudentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/students", response_model=List[Student], summary="2. Get All Students")
def get_all_students_api():
    """Returns a list of all students currently in the system."""
    return manager.get_all_students()


@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED, summary="3. Add New Student")
def create_student_api(student_data: StudentCreate):
    """Adds a new student to the system. An ID will be auto-generated if not provided."""
    try:
        # Pass the data to the manager. The manager handles ID generation and validation.
        manager.add_student(
            name=student_data.name,
            age=student_data.age,
            gender=student_data.gender,
            major=student_data.major,
            sid=student_data.sid
        )
        # Fetch the newly created student to return it in the response
        new_student = manager.get_student(student_data.sid or next(iter(manager.get_all_students()[-1].sid)))
        return new_student
    except StudentError as e:
        # Catch business logic errors (e.g., validation, ID exists)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/students/{sid}", response_model=Student, summary="4. Modify Existing Student")
def update_student_api(sid: str, student_data: StudentUpdate):
    """Modifies an existing student's information by their ID."""
    try:
        # 1. Get current data
        current_student = manager.get_student(sid)

        # 2. Apply updates (use current value if new value is None)
        new_name = student_data.name if student_data.name is not None else current_student.name
        new_age = student_data.age if student_data.age is not None else current_student.age
        new_gender = student_data.gender if student_data.gender is not None else current_student.gender
        new_major = student_data.major if student_data.major is not None else current_student.major

        # 3. Call manager's update method
        manager.update_student(sid, new_name, new_age, new_gender, new_major)

        # 4. Return the updated student object
        return manager.get_student(sid)

    except StudentError as e:
        # Catch business logic errors (e.g., validation, not found)
        if isinstance(e, StudentNotFoundError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/students/{sid}", status_code=status.HTTP_204_NO_CONTENT, summary="5. Delete Student by ID")
def delete_student_api(sid: str):
    """Deletes a student from the system by their ID."""
    try:
        manager.delete_student(sid)
        return {"message": "Student deleted successfully"}
    except StudentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StudentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/query_by_llm", response_model=LLMQueryResponse, summary="6. LLM-Driven Query (Natural Language Search)")
def llm_query_api(
    query_text: str = Query(..., description="Natural language query text, e.g., 'all females over 20'")
):
    """Parses a natural language query and returns the matching students."""
    try:
        # The manager's core filter method returns both students and the parsed parameters
        return manager._filter_students(query_text)
    except StudentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except StudentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post("/save_data", summary="7. Manually Save Data to File")
def save_data_api():
    """Manually triggers StudentManager to save in-memory data to disk."""
    try:
        manager.save_data()
        return {"message": "Data saved successfully to file!"}
    except Exception as e:
        # If saving fails (e.g., disk permission issues), return 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save data: {str(e)}")


# --- 8. Frontend Page Route ---

@app.get("/", summary="Web UI Page (Root Route)")
def serve_home(request: Request):
    """Renders the main HTML form."""
    # index.html is looked up in the templates/ folder
    return templates.TemplateResponse("index.html", {"request": request})


# --- 9. Auto-launch Server and Browser ---
if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 8000
    WEB_URL = f"http://{HOST}:{PORT}/"

    def open_browser():
        """Function to open browser after a delay"""
        time.sleep(1) # Give the server a moment to start
        webbrowser.open_new_tab(WEB_URL)

    # Start the browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    print(f"Web UI is running at: {WEB_URL}")
    print("Press Ctrl+C to stop the server.")

    # Start the FastAPI server
    uvicorn.run(app, host=HOST, port=PORT)
