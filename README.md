# STORM: Structured Topic Organization and Research Method

> Implementation of the STORM algorithm described in ["Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models"](https://arxiv.org/abs/2402.14207) (arXiv, 2024)

STORM is an advanced Python-based algorithm that implements a sophisticated approach to web research and content analysis. It combines multiple AI models and search APIs to generate comprehensive, well-structured research outlines with source attribution, following the methodology outlined in the research paper.

## 🎯 Overview

STORM helps researchers and content creators by:
1. Generating related topics for deeper exploration
2. Performing intelligent web searches
3. Analyzing and structuring content
4. Creating detailed outlines with source attribution
5. Managing research conversations and perspectives

## 🗺️ Roadmap

### Phase 1: Core Implementation - [View Source](storm.py#L27-L40)
- [x] Initialize with Gemini and Exa API clients
- [x] Environment variable configuration
- [x] Basic error handling and validation

### Phase 2: Topic Generation - [View Source](storm.py#L42-L84)
- [x] Related topic generation using Gemini
- [x] Topic relevance scoring
- [x] Intelligent topic filtering

### Phase 3: Content Gathering - [View Source](storm.py#L86-L165)
- [x] Wikipedia article fetching
- [x] Web search implementation with Exa
- [x] Content extraction and cleaning

### Phase 4: Analysis & Structure - [View Source](storm.py#L167-L220)
- [x] Content re-ranking
- [x] Structure extraction
- [x] Topic organization

### Phase 5: Future Enhancements
- [ ] Implement additional search providers
- [ ] Add support for academic papers
- [ ] Enhance outline generation
- [ ] Improve source validation

## 🛠️ Technology Stack

- **AI Models**: Google Gemini Pro
- **Search APIs**: Exa Search API
- **Content Processing**: BeautifulSoup4, NLTK
- **Environment**: Python 3.x with type hints

## 📋 Prerequisites

- Python 3.8+
- API Keys:
  - GEMINI_LLM_KEY
  - EXA_API_KEY

