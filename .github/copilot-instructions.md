<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Adobe Hackathon Challenge 1B - Document Intelligence

This is a Python-based document intelligence system for the Adobe India Hackathon 2025 Challenge 1B.

## Project Context

- **Goal**: Extract and rank relevant sections from PDF collections based on persona and job requirements
- **Constraints**: CPU-only, offline operation, <60s execution, <1GB model size
- **Output**: Structured JSON with ranked sections and subsection analysis

## Code Guidelines

- Follow Python best practices and PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all classes and methods
- Implement robust error handling and logging
- Optimize for performance and memory efficiency
- Ensure offline operation with no external API calls

## Key Components

1. **PDF Processing**: Text extraction and document parsing
2. **Text Analysis**: Section extraction and content processing
3. **Persona Matching**: Relevance scoring based on persona requirements
4. **Section Ranking**: Multi-factor scoring algorithm
5. **Output Generation**: Structured JSON output format

## Testing Approach

- Test with multiple document types and formats
- Validate output format compliance
- Performance testing under time constraints
- Edge case handling (malformed PDFs, missing sections)

When suggesting code improvements or new features, consider the hackathon constraints and focus on accuracy, performance, and reliability.
