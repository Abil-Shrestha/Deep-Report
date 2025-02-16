import os
import logging
from storm.core import STORM

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('storm_research.log'),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Make sure you have set these environment variables or use a .env file
    required_vars = ["GEMINI_LLM_KEY", "EXA_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your environment or .env file")
        return

    # Initialize STORM
    storm = STORM()

    # Get topic from user
    topic = input("Enter research topic: ")

    try:
        # Run the research pipeline
        report = storm.run(topic)

        # Print report summary
        print("\n=== Research Report ===")
        print(f"\nTitle: {report.title}")
        print(f"\nAbstract:\n{report.abstract}")
        print(f"\nKey Findings:")
        for finding in report.conclusion['summary']:
            print(f"- {finding}")
        print(f"\nWord Count: {report.word_count}")

        # Optionally save the report
        save = input("\nWould you like to save the report? (y/n): ")
        if save.lower() == 'y':
            filename = f"report_{topic.replace(' ', '_').lower()}.md"
            with open(filename, 'w') as f:
                # Title Page
                f.write(f"# {report.title}\n\n")
                
                # Abstract
                f.write("## Abstract\n\n")
                f.write(f"{report.abstract}\n\n")
                
                # Introduction
                f.write("## Introduction\n\n")
                f.write("### Background\n\n")
                f.write(f"{report.introduction['background']}\n\n")
                f.write("### Research Problem\n\n")
                f.write(f"{report.introduction['research_problem']}\n\n")
                f.write("### Objectives\n\n")
                for obj in report.introduction['objectives']:
                    f.write(f"* {obj}\n")
                f.write(f"\n### Methodology Overview\n\n")
                f.write(f"{report.introduction['methodology_overview']}\n\n")
                
                # Literature Review
                f.write("## Literature Review\n\n")
                for entry in report.literature_review:
                    f.write(f"### {entry['source']}\n\n")
                    f.write(f"{entry['summary']}\n\n")
                    f.write(f"*{entry['relevance']}*\n\n")
                
                # Methodology
                f.write("## Methodology\n\n")
                f.write("### Research Design\n\n")
                f.write(f"{report.methodology['research_design']}\n\n")
                f.write("### Data Collection Methods\n\n")
                for method in report.methodology['data_collection']:
                    f.write(f"* {method}\n")
                f.write("\n### Analysis Techniques\n\n")
                for technique in report.methodology['analysis_techniques']:
                    f.write(f"* {technique}\n")
                f.write("\n")
                
                # Results
                f.write("## Results\n\n")
                f.write("### Key Findings\n\n")
                for finding in report.results['key_findings']:
                    f.write(f"* {finding}\n")
                f.write("\n### Supporting Evidence\n\n")
                for evidence in report.results['evidence']:
                    f.write(f"* {evidence}\n")
                f.write("\n")
                
                # Discussion
                f.write("## Discussion\n\n")
                f.write("### Interpretation\n\n")
                for point in report.discussion['interpretation']:
                    f.write(f"* {point}\n")
                f.write("\n### Implications\n\n")
                for impl in report.discussion['implications']:
                    f.write(f"* {impl}\n")
                f.write("\n")
                
                # Conclusion
                f.write("## Conclusion\n\n")
                f.write("### Summary\n\n")
                for point in report.conclusion['summary']:
                    f.write(f"* {point}\n")
                f.write("\n### Limitations\n\n")
                for limit in report.conclusion['limitations']:
                    f.write(f"* {limit}\n")
                f.write("\n### Recommendations\n\n")
                for rec in report.conclusion['recommendations']:
                    f.write(f"* {rec}\n")
                f.write("\n")
                
                # References
                f.write("## References\n\n")
                for ref in report.references:
                    f.write(f"* {ref}\n")
                f.write("\n")
                
                # Appendices
                if report.appendices:
                    f.write("## Appendices\n\n")
                    for i, appendix in enumerate(report.appendices, 1):
                        f.write(f"### Appendix {i}: {appendix['title']}\n\n")
                        for item in appendix['content']:
                            f.write(f"* {item}\n")
                    f.write("\n")
                
                # Metadata
                f.write("---\n")
                f.write(f"*Word Count: {report.word_count}*\n")
            
            print(f"\nReport saved to {filename}")

    except Exception as e:
        logger.error(f"Error running research: {str(e)}")
        logger.exception("Full traceback:")

if __name__ == "__main__":
    main() 