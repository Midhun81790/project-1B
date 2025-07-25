# Adobe India Hackathon 2025 - Challenge 1B
## Persona-Driven Document Intelligence System

### Overview

This solution extracts and ranks the most relevant sections from PDF document collections based on a given persona and specific job-to-be-done requirements. The system uses advanced text analysis, persona matching, and intelligent ranking algorithms to identify the most important content for specific use cases.

### Architecture

The system consists of five core modules:

1. **PDF Processor**: Extracts structured text content from PDF documents with section identification
2. **Text Analyzer**: Performs advanced text processing and section extraction using multiple methods
3. **Persona Matcher**: Analyzes persona requirements and calculates content relevance scores
4. **Section Ranker**: Ranks sections by importance using weighted scoring algorithms
5. **Output Generator**: Produces structured JSON output in the required format

### Key Features

- **Multi-method Section Extraction**: Header-based, paragraph-based, and sliding window approaches
- **Persona-Driven Relevance Scoring**: Custom keyword matching and contextual analysis
- **Intelligent Ranking Algorithm**: Combines relevance, quality, completeness, and uniqueness scores
- **Optimized for Performance**: Processes 3-5 PDFs in under 60 seconds
- **Offline Operation**: No internet access required, uses local NLP models
- **Docker Deployment**: Containerized for consistent execution

### Usage

#### Local Development
```bash
python main.py --input ./input --output ./output
```

#### Docker Execution
```bash
docker build -t adobe-challenge-1b .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none adobe-challenge-1b
```

### Input Format

Place the following in your input directory:
- `input.json`: Configuration file with persona and job requirements
- PDF files referenced in the input.json

### Output Format

The system generates `output.json` with:
- **Metadata**: Input documents, persona, job description, processing timestamp
- **Extracted Sections**: Top-ranked sections with importance rankings
- **Subsection Analysis**: Refined text content from the most relevant sections

### Performance

- **Execution Time**: ≤ 60 seconds for 3-5 PDFs
- **Model Size**: < 1 GB (uses lightweight NLP models)
- **Resource Usage**: CPU-only, optimized for memory efficiency
- **Offline Capability**: No network access required

### Technical Implementation

- **Text Extraction**: PyMuPDF for high-quality PDF text extraction
- **NLP Processing**: NLTK for text analysis and preprocessing
- **Ranking Algorithm**: Multi-factor scoring with weighted components
- **Output Validation**: Ensures compliance with required JSON format

### Dependencies

- Python 3.11+
- PyMuPDF (document processing)
- NLTK (text analysis)
- NumPy (numerical computations)
- Standard library modules for JSON processing and file handling

This solution provides accurate, persona-driven document intelligence suitable for academic research, business analysis, technical documentation, and domain-specific use cases.
