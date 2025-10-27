# llm_query_agent.py

from typing import Dict, Any
from llm_interface import IQueryAgent
from student_model import StudentError


class LLMQueryAgent(IQueryAgent):
    """
    Concrete implementation of the LLM Query Agent (MOCK).
    In a real project, this class would handle the API call to an external LLM
    (like Gemini, OpenAI, etc.) to get a structured JSON response.
    Here, we use hardcoded logic to simulate the LLM's parsing behavior
    for architectural demonstration, fulfilling the LLM application requirement.
    """

    def parse_query(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Mocks the LLM's process of converting natural language into a structured query.
        This function demonstrates how the LLM layer abstracts API complexity
        and converts unstructured text into usable parameters for the Manager.
        """
        print(f"[{self.__class__.__name__}] Calling mock LLM API to parse: '{natural_language_text}'...")

        # --- Mocking the LLM's parsing and structured output ---
        text = natural_language_text.lower()
        query_params: Dict[str, Any] = {}

        # 1. Simulate age parsing
        if 'greater than 20' in text or 'over 20' in text or '20+' in text or '大于20' in text or '20岁以上' in text:
            query_params['age_min'] = 20
        if 'less than 18' in text or 'under 18' in text or '小于18' in text or '18岁以下' in text:
            query_params['age_max'] = 18

        # 2. Simulate gender parsing
        if 'female' in text or 'girl' in text or '女生' in text or '女性' in text:
            query_params['gender'] = 'Female'
        elif 'male' in text or 'boy' in text or '男生' in text or '男性' in text:
            query_params['gender'] = 'Male'

        # 3. Simulate major parsing (handling both English and Chinese keywords)
        if 'computer science' in text or 'cs' in text or 'software engineering' in text or '计算机' in text or '软件工程' in text:
            query_params['major'] = 'Computer Science'
        elif 'finance' in text or 'business' in text or '金融' in text:
            query_params['major'] = 'Finance'

        # 4. Handle failed/unstructured parsing
        if not query_params and ('about' in text or 'who is' in text or '关于' in text or '谁是' in text):
            raise StudentError(
                "LLM failed to extract valid filtering parameters from the natural language input. Please try a more specific query.")

        print(f"[{self.__class__.__name__}] LLM Parsed Params: {query_params}")

        if not query_params:
            raise StudentError("LLM Parsing Failed: No valid filtering conditions were recognized.")

        return query_params
