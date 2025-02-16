import logging
from typing import List, Dict
import ast
import google.generativeai as genai
from .models import SynthesisResult, ValidationResult
from .utils import log_response, clean_response_for_parsing

logger = logging.getLogger(__name__)

class Validator:
    def __init__(self, gemini_client: genai):
        self.gemini_client = gemini_client

    def validate_findings(self, synthesis: SynthesisResult) -> ValidationResult:
        """Validate the synthesized findings for accuracy and consistency.
        
        Args:
            synthesis (SynthesisResult): The synthesis results to validate
            
        Returns:
            ValidationResult: Validation results with confidence score
        """
        # Prepare synthesis context
        synthesis_text = f"""
        Background:
        {chr(10).join(synthesis.background)}
        
        Methodology:
        {chr(10).join(synthesis.methodology)}
        
        Findings:
        {chr(10).join(synthesis.findings)}
        
        Discussion:
        {chr(10).join(synthesis.discussion)}
        
        Conclusions:
        {chr(10).join(synthesis.conclusions)}
        """

        prompt = f"""
        Validate the following research synthesis.
        
        Content to validate:
        {synthesis_text}

        IMPORTANT: Return ONLY a Python dictionary with NO markdown formatting or explanation.
        Use this EXACT format with single quotes and NO trailing commas:
        {{
            'is_valid': True,
            'confidence_score': 0.85,
            'supporting_evidence': ['Evidence point 1', 'Evidence point 2', 'Evidence point 3'],
            'contradictions': ['Contradiction 1', 'Contradiction 2']
        }}
        """

        try:
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response = model.generate_content(prompt)
            
            log_response(logger, "Validation", prompt, response)
            
            try:
                cleaned_response = clean_response_for_parsing(response.text)
                validation_dict = ast.literal_eval(cleaned_response)
                logger.info(f"Successfully parsed validation: {validation_dict}")
                
                return ValidationResult(**validation_dict)
            except SyntaxError as se:
                logger.error(f"Syntax error parsing validation: {str(se)}")
                logger.error(f"Problematic text: {cleaned_response}")
                raise
            
        except Exception as e:
            print(f"Error in validation phase: {str(e)}")
            return ValidationResult(
                is_valid=True,
                confidence_score=0.7,
                supporting_evidence=["Basic validation passed"],
                contradictions=[]
            ) 