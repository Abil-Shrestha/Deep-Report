import logging
import json
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def clean_response_for_parsing(response_text: str) -> str:
    """Clean the model's response text for parsing."""
    # Remove markdown code blocks if present
    if '```' in response_text:
        # Extract content between code blocks
        start = response_text.find('```') + 3
        end = response_text.rfind('```')
        # Skip the language identifier if present (e.g., ```python)
        if 'python' in response_text[start:start+6].lower():
            start = response_text.find('\n', start) + 1
        response_text = response_text[start:end].strip()
    
    # If response is not in the expected format, try to create a valid Python literal
    if not (response_text.startswith('{') or response_text.startswith('[')):
        # For list responses
        if 'finding' in response_text.lower():
            return "['Unable to parse model response']"
        # For dict responses
        return "{'error': 'Unable to parse model response'}"
    
    return response_text.strip()

def log_response(logger: logging.Logger, step: str, prompt: str, response: Any, error: Exception = None):
    """Log the prompt, response, and any errors from a model interaction."""
    logger.info(f"\n{'='*50}\n{step} Step\n{'='*50}")
    logger.info(f"Prompt:\n{prompt}")
    
    if response:
        logger.info(f"Raw Response:\n{response.text}")
        cleaned = clean_response_for_parsing(response.text)
        logger.info(f"Cleaned Response:\n{cleaned}")
        try:
            # Try to format the response for better readability
            logger.info(f"Formatted Response:\n{json.dumps(cleaned, indent=2)}")
        except:
            pass
    
    if error:
        logger.error(f"Error:\n{str(error)}\n")
        if hasattr(error, '__traceback__'):
            logger.error(f"Traceback:\n{error.__traceback__}") 