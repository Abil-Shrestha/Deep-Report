from typing import List
from storm import Conversation
import os
from datetime import datetime

def generate_markdown_report(topic: str, outline: List[str], conversations: List[Conversation], output_dir: str = ".") -> str:
    """Generate a markdown report from the STORM analysis results.
    
    Args:
        topic (str): The main topic of the report
        outline (List[str]): The final outline points
        conversations (List[Conversation]): The conversations that led to insights
        output_dir (str): Directory to save the report in
        
    Returns:
        str: Path to the generated report file
    """
    # Create report filename based on topic and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic.lower())
    filename = f"report_{safe_topic}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Generate report content
    report = [
        f"# {topic.title()}\n",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "## Executive Summary\n",
        "This report provides a comprehensive analysis of the topic, incorporating multiple perspectives and insights gathered through advanced research.\n",
        "## Table of Contents\n"
    ]
    
    # Add outline points to TOC
    for point in outline:
        # Remove any numbering from the start and clean up
        clean_point = point.lstrip("0123456789. ")
        report.append(f"- [{clean_point}](#{clean_point.lower().replace(' ', '-')})\n")
    
    report.append("\n## Detailed Analysis\n")
    
    # Add each outline point with relevant conversation insights
    for point in outline:
        clean_point = point.lstrip("0123456789. ")
        report.append(f"\n### {clean_point}\n")
        
        # Find relevant insights from conversations
        relevant_insights = []
        for conv in conversations:
            for q, a in zip(conv.questions, conv.answers):
                # Check if this Q&A pair is relevant to the current outline point
                if any(keyword in q.lower() for keyword in clean_point.lower().split()):
                    relevant_insights.append((q, a))
        
        # Add insights if found
        if relevant_insights:
            for q, a in relevant_insights:
                report.append(f"\n**Key Question**: {q}\n")
                report.append(f"\n{a}\n")
        
    # Write the report to file
    with open(filepath, "w") as f:
        f.write("".join(report))
    
    return filepath
