import os
from storm import STORM
from dotenv import load_dotenv
from report_generator import generate_markdown_report

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.getenv('TAVILY_API_KEY'):
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    if not os.getenv('GEMINI_LLM_KEY'):
        raise ValueError("GEMINI_LLM_KEY not found in environment variables")
    
    # Create STORM instance
    storm = STORM()
    
    # Define the topic
    topic = "create a report about the best league of legend champs for URF"
    
    # Run STORM analysis
    print("\n=== Starting STORM Analysis ===\n")
    outline, conversations = storm.run(
        topic=topic,
        max_perspectives=4,  # Increased for better coverage
        max_rounds=2
    )
    
    # Generate markdown report
    report_path = generate_markdown_report(topic, outline, conversations)
    print(f"\n=== Report generated: {report_path} ===\n")
    
    # Print outline for reference
    print("\n=== Final Outline ===\n")
    for point in outline:
        print(point)

if __name__ == "__main__":
    main()
