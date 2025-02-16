from typing import Dict, Any
import os
from dotenv import load_dotenv
import google.generativeai as genai
from exa_py import Exa

from .models import (
    ResearchPlan, ResearchResult, AnalysisResult,
    SynthesisResult, ValidationResult, Report
)
from .planning import Planner
from .research import Researcher
from .analysis import Analyzer
from .synthesis import Synthesizer
from .validation import Validator

class STORM:
    def __init__(self):
        """Initialize STORM by loading API keys and setting up models."""
        load_dotenv()
        
        gemini_api_key = os.getenv("GEMINI_LLM_KEY")
        exa_api_key = os.getenv("EXA_API_KEY")
        
        if not gemini_api_key or not exa_api_key:
            raise ValueError("Missing required API keys")

        # Initialize Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        
        # Initialize Exa
        self.exa_client = Exa(exa_api_key)
        
        # Initialize components
        self.planner = Planner(model)
        self.researcher = Researcher(model, self.exa_client)
        self.analyzer = Analyzer(model)
        self.synthesizer = Synthesizer(model)
        self.validator = Validator(model)
        
        self.max_words = 10000

    def run(self, topic: str) -> Report:
        """Execute the STORM research and analysis pipeline."""
        print("Phase 1: Planning...")
        plan = self.planner.create_plan(topic)
        
        print("Phase 2: Research...")
        research_results = self.researcher.conduct_research(topic, plan)
        
        print("Phase 3: Analysis...")
        analysis_results = self.analyzer.analyze_findings(topic, research_results)
        
        print("Phase 4: Synthesis...")
        synthesis_results = self.synthesizer.synthesize_results(topic, analysis_results)
        
        print("Phase 5: Validation...")
        validation_results = self.validator.validate_findings(synthesis_results)
        
        print("Generating final report...")
        return self._generate_report(topic, research_results, analysis_results, 
                                   synthesis_results, validation_results)

    def _generate_report(self, topic: str, research: ResearchResult, 
                        analysis: AnalysisResult, synthesis: SynthesisResult, 
                        validation: ValidationResult) -> Report:
        """Generate the final report from all components' results."""
        
        # Generate title
        title = f"Research Analysis: {topic.title()}"
        
        # Generate abstract using Gemini
        abstract_prompt = f"""
        Create a comprehensive 250-word abstract summarizing this research on {topic}.
        
        Include these elements, with each being 4-5 substantial sentences:
        1. Research context and problem statement
        2. Methodology and approach used
        3. Key findings: {', '.join(research.key_findings[:3])}
        4. Main implications: {', '.join(analysis.implications[:2])}
        5. Conclusions and recommendations
        
        IMPORTANT: 
        - Return a single cohesive paragraph
        - Each aspect should be thoroughly explained
        - Use clear transitions between elements
        - No formatting or markers
        - Aim for academic tone and style
        """
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response = model.generate_content(abstract_prompt)
            abstract = response.text.strip()
        except Exception as e:
            logger.error(f"Error generating abstract: {str(e)}")
            abstract = f"A comprehensive study examining {topic}, analyzing key aspects and implications."

        # Enhance introduction background
        background_prompt = f"""
        Write a substantial 4-5 sentence paragraph providing background context for research on {topic}.
        Include historical context, current relevance, and significance of the research area.
        """
        try:
            background_response = model.generate_content(background_prompt)
            background = background_response.text.strip()
        except Exception as e:
            background = f"This research explores {topic}."

        introduction = {
            "background": background,
            "research_problem": research.key_findings[0] if research.key_findings else 
                              f"Understanding the complexities of {topic}",
            "objectives": [obj for obj in research.methodology.split('. ') if obj],
            "methodology_overview": research.methodology
        }

        # Enhance methodology description
        methodology_prompt = f"""
        Write a detailed 4-5 sentence paragraph describing the research methodology for {topic}.
        Include rationale for chosen methods, data collection approach, and analysis framework.
        """
        try:
            methodology_response = model.generate_content(methodology_prompt)
            methodology_text = methodology_response.text.strip()
        except Exception as e:
            methodology_text = research.methodology

        methodology = {
            "research_design": methodology_text,
            "data_collection": [
                "Web-based research using academic and industry sources",
                "Analysis of current literature and expert opinions",
                "Systematic review of available data"
            ],
            "analysis_techniques": [
                "Content analysis of gathered information",
                "Thematic analysis of key findings",
                "Validation through cross-referencing multiple sources"
            ]
        }

        # Prepare literature review
        literature_review = []
        for source in research.sources[:5]:
            if source.title and source.content:
                review_entry = {
                    "source": source.title,
                    "summary": source.content[:500] + "...",
                    "relevance": f"Relevance score: {source.relevance_score:.2f}"
                }
                literature_review.append(review_entry)

        # Prepare results section
        results = {
            "key_findings": research.key_findings,
            "evidence": analysis.evidence,
            "data_points": synthesis.findings
        }

        # Prepare discussion section
        discussion = {
            "interpretation": synthesis.discussion,
            "implications": analysis.implications,
            "comparisons": [point for point in analysis.key_points if "compared" in point.lower()]
        }

        # Prepare conclusion
        conclusion = {
            'summary': synthesis.conclusions,
            'limitations': validation.contradictions if validation.contradictions else 
                         ["No significant limitations identified"],
            'recommendations': [impl for impl in analysis.implications if "should" in impl.lower() or 
                              "could" in impl.lower() or "recommend" in impl.lower()]
        }

        # Prepare references
        references = [
            f"{s.title}. Retrieved from {s.url}" 
            for s in research.sources if s.title and s.url
        ]

        # Prepare appendices
        appendices = []
        if validation.supporting_evidence:
            appendices.append({
                "title": "Supporting Evidence",
                "content": validation.supporting_evidence
            })
        if validation.contradictions:
            appendices.append({
                "title": "Identified Contradictions and Gaps",
                "content": validation.contradictions
            })

        # Create the report
        report = Report(
            title=title,
            abstract=abstract,
            introduction=introduction,
            literature_review=literature_review,
            methodology=methodology,
            results=results,
            discussion=discussion,
            conclusion=conclusion,
            references=references,
            appendices=appendices,
            word_count=0  # Will be calculated below
        )

        # Calculate word count
        def count_words(text) -> int:
            if isinstance(text, list):
                return sum(count_words(item) for item in text)
            elif isinstance(text, dict):
                return sum(count_words(value) for value in text.values())
            elif isinstance(text, str):
                return len(text.split())
            return 0

        report.word_count = count_words(abstract) + \
                           count_words(introduction) + \
                           count_words(literature_review) + \
                           count_words(methodology) + \
                           count_words(results) + \
                           count_words(discussion) + \
                           count_words(conclusion) + \
                           count_words(references)

        return report 