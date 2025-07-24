# Adobe "Connecting the Dots" Hackathon Solutions

## Overview

This repository contains comprehensive solutions for Adobe's "Connecting the Dots" Challenge, focusing on intelligent PDF document processing and analysis.

## Challenge Solutions

### 🔍 [Challenge 1A: PDF Outline Extraction](README_Challenge1A.md)
**Goal**: Extract structured outlines (title, H1/H2/H3 headings) from PDF documents

**Key Features**:
- Multi-layered heading detection using pattern matching and font analysis
- Intelligent title extraction with metadata fallback
- Performance optimized for 50-page documents in <10 seconds
- Robust handling of various document formats

**Technologies**: PyMuPDF, Python 3.9, Docker

---

### 🧠 [Challenge 1B: Persona-Driven Document Intelligence](README_Challenge1B.md)  
**Goal**: Analyze document collections and extract relevant sections based on persona and job requirements

**Key Features**:
- Advanced relevance scoring with TF-IDF analysis
- Persona-specific content boosting (Travel Planner, Student, Analyst, etc.)
- Multi-document collection processing (3-10 PDFs)
- Intelligent content ranking and refinement

**Technologies**: PyMuPDF, Advanced NLP, Python 3.9, Docker

## Quick Start

### Challenge 1A - PDF Outline Extraction

```bash
# Build
docker build --platform linux/amd64 -f Dockerfile.challenge1a -t challenge1a:latest .

# Run  
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1a:latest
```

### Challenge 1B - Document Intelligence

```bash
# Build
docker build --platform linux/amd64 -f Dockerfile.challenge1b -t challenge1b:latest .

# Run
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1b:latest
```

## Repository Structure

```
├── challenge1a_solution.py     # Challenge 1A implementation
├── challenge1b_solution.py     # Challenge 1B implementation
├── Dockerfile.challenge1a      # Docker config for Challenge 1A
├── Dockerfile.challenge1b      # Docker config for Challenge 1B
├── README.md                   # This file
├── README_Challenge1A.md       # Detailed Challenge 1A documentation
└── README_Challenge1B.md       # Detailed Challenge 1B documentation
```

## Solution Highlights

### 🚀 Performance
- **Challenge 1A**: <10 seconds for 50-page PDFs
- **Challenge 1B**: <60 seconds for 3-5 document collections
- **Memory**: Optimized for 8 CPU, 16GB RAM systems
- **Model Size**: Compliant with size constraints (200MB/1GB)

### 🎯 Accuracy
- **Advanced Pattern Recognition**: Handles diverse document formats
- **Multi-signal Analysis**: Combines font, content, and context clues
- **Persona Intelligence**: Adapts to different user roles and requirements
- **Quality Filtering**: Ensures meaningful content extraction

### 🔧 Technical Excellence
- **CPU-only Processing**: No GPU dependencies
- **Offline Operation**: No internet connectivity required
- **Docker Containerized**: AMD64 architecture support
- **Robust Error Handling**: Graceful processing of varied inputs

## Key Algorithms

### Challenge 1A: Hierarchical Heading Detection
```
Heading Score = Pattern Match + Font Size Analysis + Formatting Boost
Final Level = Classify based on total score and context
```

### Challenge 1B: Persona-Driven Relevance
```
Relevance = (Keyword Overlap × 0.4) + (TF-IDF × 0.3) + (Context Boost × 0.3)
Final Score = Relevance × Content Quality Factor
```

## Testing

Both solutions have been thoroughly tested with:
- ✅ Sample datasets provided by Adobe
- ✅ Various document types (forms, guides, tutorials, reports)
- ✅ Different persona scenarios (Travel, Business, Education, HR)
- ✅ Performance benchmarks and accuracy validation

## Dependencies

- **PyMuPDF (1.23.26)**: PDF processing and text extraction
- **Python 3.9**: Core runtime environment  
- **pathlib**: Modern file system operations
- **Standard Library**: json, re, datetime, collections, math

## Compliance

- ✅ **Docker**: AMD64 platform compatibility
- ✅ **Performance**: Meets all timing constraints
- ✅ **Security**: No network access, secure processing
- ✅ **Standards**: Follows JSON schema specifications
- ✅ **Open Source**: Uses only open-source libraries

## Future Enhancements

### Round 2 Preparation
These solutions are designed to be modular and reusable for Round 2's web application development using Adobe's PDF Embed API. The extracted outlines and intelligent content analysis will power:

- Interactive document navigation
- Smart content recommendations
- Persona-based reading experiences
- Cross-document insight generation

---

**Built for Adobe's "Connecting the Dots" Challenge 2025**

*Transforming how we read, learn, and connect with documents through intelligent analysis and user-centered design.*