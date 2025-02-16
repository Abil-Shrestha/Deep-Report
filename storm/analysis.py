import logging
from typing import List
import ast
import google.generativeai as genai
from .models import ResearchResult, AnalysisResult
from .utils import log_response, clean_response_for_parsing

logger = logging.getLogger(__name__)

class Analyzer:
    def __init__(self, gemini_client: genai):
        self.gemini_client = gemini_client

    def analyze_findings(self, topic: str, research: ResearchResult) -> AnalysisResult:
        """Analyze research findings to identify key points, evidence, and implications.
        
        Args:
            topic (str): The research topic
            research (ResearchResult): The research results to analyze
            
        Returns:
            AnalysisResult: Structured analysis of the research
        """
        # Prepare research context
        findings_text = "\n".join(f"- {finding}" for finding in research.key_findings)
        sources_text = "\n\n".join(
            f"Source: {s.title}\nContent: {s.content[:300]}..."
            for s in research.sources[:5]
        )

        prompt = f"""
        Analyze these research findings about {topic}:
        
        Key Findings:
        {findings_text}

        Supporting Sources:
        {sources_text}

        IMPORTANT: Return ONLY a Python dictionary with NO markdown formatting or explanation.
        Use this EXACT format with single quotes and NO trailing commas:
        {{
            'key_points': ['Main point 1 about {topic}', 'Main point 2 about {topic}', 'Main point 3 about {topic}'],
            'evidence': ['Evidence 1 from sources', 'Evidence 2 from sources', 'Evidence 3 from sources'],
            'implications': ['Implication 1 for {topic}', 'Implication 2 for {topic}', 'Implication 3 for {topic}']
        }}
        """

        try:
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response = model.generate_content(prompt)
            
            log_response(logger, "Analysis", prompt, response)
            
            try:
                cleaned_response = clean_response_for_parsing(response.text)
                analysis_dict = ast.literal_eval(cleaned_response)
                logger.info(f"Successfully parsed analysis: {analysis_dict}")
                
                return AnalysisResult(
                    topic=topic,
                    key_points=analysis_dict['key_points'],
                    evidence=analysis_dict['evidence'],
                    implications=analysis_dict['implications']
                )
            except SyntaxError as se:
                logger.error(f"Syntax error parsing analysis: {str(se)}")
                logger.error(f"Problematic text: {cleaned_response}")
                raise
            
        except Exception as e:
            print(f"Error in analysis phase: {str(e)}")
            return AnalysisResult(
                topic=topic,
                key_points=[f"Key point about {topic}"],
                evidence=[f"Evidence from research on {topic}"],
                implications=[f"Potential implication of {topic}"]
            ) 