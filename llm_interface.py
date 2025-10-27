# llm_interface.py

from abc import ABC, abstractmethod
from typing import Dict, Any

class IQueryAgent(ABC):
    """
    Dependency Inversion Principle (DIP): Defines the abstraction for the Natural Language Query Agent.
    StudentManager will depend on this interface.
    """

    @abstractmethod
    def parse_query(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Parses natural language text into a structured query dictionary
        (e.g., {'age_min': 20, 'major': 'CS'}).
        Should raise StudentError if parsing fails or input is incomprehensible.
        """
        pass
