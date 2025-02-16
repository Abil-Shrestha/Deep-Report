from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from exa_py import Exa
from .models import ResearchPlan, ResearchResult, ResearchSource
import ast
import logging
from .utils import log_response, clean_response_for_parsing

logger = logging.getLogger(__name__)

class Researcher:
    def __init__(self, gemini_client: genai, exa_client: Exa):
        self.gemini_client = gemini_client
        self.exa_client = exa_client

    def conduct_research(self, topic: str, plan: ResearchPlan) -> ResearchResult:
        """Conduct research based on the research plan.
        
        Args:
            topic (str): The research topic
            plan (ResearchPlan): The research plan
            
        Returns:
            ResearchResult: Research findings and sources
        """
        sources = []
        
        # Conduct web research for each research question
        for question in plan.questions:
            search_results = self._web_search(f"{topic} {question}")
            for result in search_results:
                source = ResearchSource(
                    title=result['title'],
                    content=result['content'],
                    url=result['url'],
                    relevance_score=float(result.get('score', 0)),
                    publication_date=result.get('published_date')
                )
                sources.append(source)

        # Extract key findings using Gemini
        key_findings = self._extract_findings(topic, sources)
        
        return ResearchResult(
            topic=topic,
            sources=sources,
            key_findings=key_findings,
            methodology=plan.methodology
        )

    def _web_search(self, query: str) -> List[Dict]:
        """Perform web search using Exa API."""
        try:
            response = self.exa_client.search_and_contents(
                query,
                num_results=3,
                highlights={"num_sentences": 4},
                use_autoprompt=True
            )
            
            return [{
                'url': result.url,
                'title': result.title,
                'content': result.highlights[0] if result.highlights else result.text,
                'score': float(result.score) if hasattr(result, 'score') and result.score is not None else 0.0,
                'published_date': result.published_date if hasattr(result, 'published_date') else None
            } for result in response.results]
            
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return []

    def _extract_findings(self, topic: str, sources: List[ResearchSource]) -> List[str]:
        """Extract key findings from sources using Gemini."""
        sources_text = "\n\n".join(
            f"Source: {s.title}\nContent: {s.content[:500]}..." 
            for s in sources[:5]
        )

        prompt = f"""
        Based on these sources about {topic}, identify 5-7 key findings.
        
        Sources:
        {sources_text}

        IMPORTANT: Return ONLY a Python list with NO markdown formatting or explanation.
        Use this EXACT format with single quotes and NO trailing commas:
        [
            'First key finding about {topic}',
            'Second key finding about {topic}',
            'Third key finding about {topic}'
        ]
        """

        try:
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response = model.generate_content(prompt)
            
            # Log the response
            log_response(logger, "Research", prompt, response)
            
            try:
                cleaned_response = clean_response_for_parsing(response.text)
                findings = ast.literal_eval(cleaned_response)
                logger.info(f"Successfully parsed findings: {findings}")
                return findings if isinstance(findings, list) else []
            except SyntaxError as se:
                logger.error(f"Syntax error parsing findings: {str(se)}")
                logger.error(f"Problematic text: {cleaned_response}")
                raise
            
        except Exception as e:
            print(f"Error extracting findings: {str(e)}")
            return [f"Finding about {topic} from available sources"] 