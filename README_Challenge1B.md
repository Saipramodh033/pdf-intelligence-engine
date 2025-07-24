# Challenge 1B: Persona-Driven Document Intelligence Solution

## Overview

This solution analyzes collections of PDF documents and extracts the most relevant sections based on specific persona requirements and job-to-be-done tasks. It uses advanced text analysis, relevance scoring, and persona-aware content ranking.

## Approach

### 1. Intelligent Section Extraction
- **Hierarchical Parsing**: Identifies document sections using heading patterns and content structure
- **Context-Aware Segmentation**: Groups related content into meaningful sections
- **Multi-page Processing**: Handles sections spanning multiple pages

### 2. Persona-Driven Relevance Scoring
- **Keyword Overlap Analysis**: Matches persona/job keywords with section content
- **TF-IDF Scoring**: Calculates term frequency-inverse document frequency for relevance
- **Context Boost System**: Applies persona-specific scoring multipliers
- **Content Quality Assessment**: Considers section length and substance

### 3. Advanced Ranking Algorithm
```
Final Score = (Keyword Overlap × 0.4) + (TF-IDF Score × 0.3) + (Context Boost × 0.3) × Length Penalty
```

## Key Features

### Persona-Specific Intelligence
- **Travel Planner**: Boosts content about itinerary, accommodation, activities, restaurants
- **Student**: Emphasizes study materials, concepts, theories, examples
- **Business Analyst**: Prioritizes revenue, market analysis, financial data
- **HR Professional**: Focuses on forms, processes, compliance, policies
- **Food Contractor**: Highlights recipes, ingredients, menu planning

### Multi-Document Analysis
- Processes 3-10 related PDFs simultaneously
- Maintains document source tracking
- Cross-document relevance comparison
- Unified ranking across entire collection

### Intelligent Content Refinement
- Extracts most relevant subsections with detailed content
- Truncates overly long content intelligently
- Preserves key information while maintaining readability
- Provides page-level granularity for source reference

## Technical Architecture

### Core Components

1. **PDFTextExtractor**: Extracts and organizes text by page
2. **SectionParser**: Identifies document structure and sections
3. **RelevanceCalculator**: Computes multi-factor relevance scores
4. **PersonaAnalyzer**: Applies persona-specific logic and boosts
5. **ContentRanker**: Sorts and selects top relevant sections

### Scoring Methodology

#### Keyword Overlap Score
- Extracts meaningful keywords from persona and job description
- Removes stop words and short terms
- Calculates intersection percentage with section content

#### TF-IDF Analysis
- Term frequency within section content
- Inverse document frequency approximation
- Normalized by keyword count for fairness

#### Context Boost Factors
- Domain-specific terminology recognition
- Job-specific keyword matching
- Title vs content weighting (title gets higher boost)
- Cumulative scoring with caps to prevent over-inflation

## Libraries Used

- **PyMuPDF (fitz)**: PDF text extraction and page processing
- **pathlib**: Modern file system operations
- **json**: Input/output data handling
- **datetime**: Timestamp generation
- **collections**: Data structure utilities
- **re**: Advanced pattern matching
- **math**: Mathematical calculations for scoring

## Performance Characteristics

- **Processing Speed**: ≤60 seconds for 3-5 document collections
- **Memory Efficiency**: Optimized for large document sets
- **Accuracy**: High precision in relevance ranking
- **Scalability**: Handles documents up to 50 pages each

## Docker Integration

**Configuration**:
- Base: Python 3.9 slim (AMD64)
- Model Size: <1GB constraint compliance
- CPU-only execution
- No internet dependencies

## Build & Run Instructions

### Build
```bash
docker build --platform linux/amd64 -f Dockerfile.challenge1b -t challenge1b:latest .
```

### Run
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1b:latest
```

## Input/Output Format

### Input (challenge1b_input.json)
```json
{
  "documents": [
    {"filename": "document.pdf", "title": "Document Title"}
  ],
  "persona": {"role": "Travel Planner"},
  "job_to_be_done": {"task": "Plan a 4-day trip for college friends"}
}
```

### Output (challenge1b_output.json)
```json
{
  "metadata": {
    "input_documents": ["list of files"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a 4-day trip...",
    "processing_timestamp": "2025-07-24T00:36:52.311748"
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Relevant Section",
      "importance_rank": 1,
      "page_number": 5
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf",
      "refined_text": "Detailed content...",
      "page_number": 5
    }
  ]
}
```

## Testing & Validation

### Test Collections
1. **Travel Planning**: 7 South of France guides for college trip planning
2. **Adobe Acrobat Learning**: 15 tutorials for HR form creation
3. **Recipe Collection**: 9 cooking guides for vegetarian buffet planning

### Quality Metrics
- **Section Relevance**: How well selected sections match persona needs
- **Sub-section Quality**: Accuracy of granular content extraction
- **Ranking Precision**: Correct importance ordering of results

## Algorithm Strengths

1. **Adaptive Scoring**: Adjusts to different persona types and document domains
2. **Multi-signal Analysis**: Combines multiple relevance indicators
3. **Quality Filtering**: Ensures substantial, meaningful content selection
4. **Scalable Design**: Handles varying document collection sizes
5. **Robust Processing**: Graceful handling of diverse PDF formats and structures