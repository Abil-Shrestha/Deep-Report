import logging
from typing import List
import ast
import google.generativeai as genai
from .models import ResearchPlan
from .utils import log_response, clean_response_for_parsing

logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, gemini_client: genai):
        self.gemini_client = gemini_client

    def create_plan(self, topic: str) -> ResearchPlan:
        """Create a research plan for the given topic.
        
        Args:
            topic (str): The research topic
            
        Returns:
            ResearchPlan: A structured research plan
        """
        prompt = f"""
        Create a comprehensive research plan for the topic: {topic}
        
        IMPORTANT: Return ONLY a Python dictionary with NO markdown formatting or explanation.
        Use this EXACT format with single quotes and NO trailing commas:
        {{
            'objectives': ['objective 1', 'objective 2', 'objective 3'],
            'questions': ['question 1', 'question 2', 'question 3'],
            'methodology': 'detailed description of research methodology',
            'areas': ['area 1', 'area 2', 'area 3'],
            'sources': ['source 1', 'source 2', 'source 3']
        }}
        """

        try:
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response = model.generate_content(prompt)
            
            # Log the response
            log_response(logger, "Planning", prompt, response)
            
            try:
                cleaned_response = clean_response_for_parsing(response.text)
                plan_dict = ast.literal_eval(cleaned_response)
                logger.info(f"Successfully parsed response into dictionary: {plan_dict}")
            except SyntaxError as se:
                logger.error(f"Syntax error parsing response: {str(se)}")
                logger.error(f"Problematic text: {cleaned_response}")
                raise
            
            return ResearchPlan(
                objectives=plan_dict['objectives'],
                questions=plan_dict['questions'],
                methodology=plan_dict['methodology'],
                areas=plan_dict['areas'],
                sources=plan_dict['sources']
            )
            
        except Exception as e:
            logger.error(f"Error in planning phase: {str(e)}")
            logger.exception("Full traceback:")
            # Return fallback plan
            return ResearchPlan(
                objectives=[f"Understand the fundamentals of {topic}"],
                questions=[f"What is {topic}?"],
                methodology="Basic research methodology",
                areas=["General overview"],
                sources=["Web resources"]
            ) 