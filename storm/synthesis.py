import logging
from typing import List, Dict
import ast
import google.generativeai as genai
from .models import AnalysisResult, SynthesisResult
from .utils import log_response, clean_response_for_parsing

logger = logging.getLogger(__name__)

class Synthesizer:
    def __init__(self, gemini_client: genai):
        self.gemini_client = gemini_client

    def synthesize_results(self, topic: str, analysis: AnalysisResult) -> SynthesisResult:
        """Synthesize analysis results into a coherent narrative structure.
        
        Args:
            topic (str): The research topic
            analysis (AnalysisResult): The analysis results to synthesize
            
        Returns:
            SynthesisResult: Structured synthesis of the analysis
        """
        # Prepare analysis context
        analysis_text = f"""
        Key Points:
        {chr(10).join(f'- {point}' for point in analysis.key_points)}
        
        Evidence:
        {chr(10).join(f'- {evidence}' for evidence in analysis.evidence)}
        
        Implications:
        {chr(10).join(f'- {impl}' for impl in analysis.implications)}
        """

        prompt = f"""
        Synthesize this analysis about {topic} into a coherent narrative structure.
        
        Analysis:
        {analysis_text}

        IMPORTANT: Return ONLY a Python dictionary with NO markdown formatting or explanation.
        Use this EXACT format with single quotes and NO trailing commas:
        {{
            'background': ['Background paragraph 1 about {topic}', 'Background paragraph 2 about {topic}'],
            'methodology': ['Methodology step 1', 'Methodology step 2'],
            'findings': ['Key finding 1 about {topic}', 'Key finding 2 about {topic}'],
            'discussion': ['Discussion point 1', 'Discussion point 2'],
            'conclusions': ['Conclusion 1 about {topic}', 'Conclusion 2 about {topic}']
        }}
        """

        try:
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response = model.generate_content(prompt)
            
            log_response(logger, "Synthesis", prompt, response)
            
            try:
                cleaned_response = clean_response_for_parsing(response.text)
                synthesis_dict = ast.literal_eval(cleaned_response)
                logger.info(f"Successfully parsed synthesis: {synthesis_dict}")
                
                return SynthesisResult(**synthesis_dict)
            except SyntaxError as se:
                logger.error(f"Syntax error parsing synthesis: {str(se)}")
                logger.error(f"Problematic text: {cleaned_response}")
                raise
            
        except Exception as e:
            print(f"Error in synthesis phase: {str(e)}")
            return SynthesisResult(
                background=[f"Background on {topic}"],
                methodology=["Research methodology"],
                findings=[f"Key findings about {topic}"],
                discussion=[f"Discussion of {topic}"],
                conclusions=[f"Conclusions about {topic}"]
            ) 