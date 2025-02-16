# STORM: Structured Topic-Oriented Research Machine

STORM is a comprehensive research pipeline designed to automate the process of generating detailed research reports on any given topic. It leverages advanced AI models to plan, conduct, analyze, synthesize, and validate research, producing a structured report in markdown format.

## Features

- **Automated Research Planning**: Generates a research plan with objectives, questions, methodology, and sources.
- **Web-Based Research**: Conducts web searches to gather relevant information and sources.
- **In-Depth Analysis**: Analyzes findings to identify key points, evidence, and implications.
- **Coherent Synthesis**: Synthesizes analysis results into a structured narrative.
- **Validation**: Validates the synthesized findings for accuracy and consistency.
- **Comprehensive Reporting**: Generates a markdown report with sections like Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References, and Appendices.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/storm.git
   cd storm
   ```

2. **Set Up Environment**:
   Ensure you have Python 3.8+ installed. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**:
   Create a `.env` file in the root directory and add your API keys:
   ```
   GEMINI_LLM_KEY=your_gemini_api_key
   EXA_API_KEY=your_exa_api_key
   ```

## Usage

1. **Run the STORM Pipeline**:
   Execute the main script to start the research process:
   ```bash
   python main.py
   ```

2. **Enter Research Topic**:
   When prompted, enter the topic you wish to research.

3. **View and Save Report**:
   After the pipeline completes, view the report summary in the console. You will be prompted to save the full report in markdown format.

## Report Structure

The generated report includes the following sections:

- **Title Page**: Title of the report.
- **Abstract**: A concise summary of the research.
- **Introduction**: Background, research problem, objectives, and methodology overview.
- **Literature Review**: Summary and analysis of existing research.
- **Methodology**: Detailed description of research design and methods.
- **Results**: Presentation of findings with supporting evidence.
- **Discussion**: Interpretation of results and implications.
- **Conclusion**: Summary of key findings, limitations, and recommendations.
- **References**: List of all sources cited.
- **Appendices**: Supplementary material.

## Logging

All operations and errors are logged to `storm_research.log` for debugging and review.

