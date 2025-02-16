from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class ResearchSource:
    title: str
    content: str
    url: str
    relevance_score: float
    publication_date: Optional[str] = None

@dataclass
class ResearchPlan:
    objectives: List[str]
    questions: List[str]
    methodology: str
    areas: List[str]
    sources: List[str]

@dataclass
class ResearchResult:
    topic: str
    sources: List[ResearchSource]
    key_findings: List[str]
    methodology: str

@dataclass
class AnalysisResult:
    topic: str
    key_points: List[str]
    evidence: List[str]
    implications: List[str]

@dataclass
class SynthesisResult:
    background: List[str]
    methodology: List[str]
    findings: List[str]
    discussion: List[str]
    conclusions: List[str]

@dataclass
class ValidationResult:
    is_valid: bool
    confidence_score: float
    supporting_evidence: List[str]
    contradictions: List[str]

@dataclass
class Report:
    title: str
    abstract: str
    introduction: Dict[str, Any]
    literature_review: List[Dict[str, str]]
    methodology: Dict[str, Any]
    results: Dict[str, List[str]]
    discussion: Dict[str, List[str]]
    conclusion: Dict[str, List[str]]
    references: List[str]
    appendices: List[Dict[str, Any]]
    word_count: int = 0 