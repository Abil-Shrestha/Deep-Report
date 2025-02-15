# STORM Algorithm Implementation

This is a Python implementation of the STORM (Self-reflective Tuning through Outline-assisted Retrieval Method) algorithm. The algorithm generates comprehensive outlines and references for a given topic by discovering multiple perspectives and simulating conversations.

## Features

- Topic-based perspective discovery
- Wikipedia article retrieval and parsing
- Question-answer simulation using transformers
- Outline generation and refinement
- Reference tracking

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from storm import STORM

# Initialize STORM with your API key
storm = STORM(api_key="your-api-key")

# Run the algorithm on a topic
outline, references = storm.run(
    topic="artificial intelligence",
    max_perspectives=3,
    max_rounds=2
)

# Print results
print("Outline:")
for point in outline:
    print(f"- {point}")

print("\nReferences:")
for ref in references:
    print(f"- {ref}")
```

## Components

- `Perspective`: Dataclass for storing perspective information
- `Conversation`: Dataclass for storing conversation history
- `STORM`: Main class implementing the algorithm
  - `gen_related_topics`: Generate related topics
  - `get_wiki_article`: Fetch Wikipedia articles
  - `extract_toc`: Extract table of contents
  - `gen_perspectives`: Generate perspectives
  - `gen_qn`: Generate questions
  - `gen_queries`: Generate search queries
  - `search_and_sift`: Search and filter sources
  - `gen_ans`: Generate answers
  - `direct_gen_outline`: Generate initial outline
  - `refine_outline`: Refine outline based on conversations

## Note

This implementation includes placeholder functions for certain components (e.g., knowledge graph queries, search API) that would need to be replaced with actual implementations in a production environment.
