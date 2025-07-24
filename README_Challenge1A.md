# Challenge 1A: PDF Outline Extraction Solution

## Overview

This solution extracts structured outlines (title and headings H1/H2/H3) from PDF documents with high accuracy and performance. It uses advanced text analysis techniques combined with font formatting detection to identify document structure.

## Approach

### 1. Multi-layered Heading Detection
- **Pattern Matching**: Uses regex patterns to identify common heading formats (Chapter X, numbered sections, roman numerals)
- **Font Analysis**: Analyzes font size, boldness, and formatting to classify heading levels
- **Context Scoring**: Combines multiple signals to determine heading hierarchy

### 2. Intelligent Title Extraction
- Attempts to extract title from PDF metadata first
- Falls back to content analysis of first substantial text
- Filters out headers, footers, and page numbers

### 3. Hierarchical Classification
- **H1**: Major sections, chapters, high-importance headings
- **H2**: Sub-sections, medium font size increases
- **H3**: Minor sections, slight formatting emphasis

## Key Features

- **Robust Pattern Recognition**: Handles various document formats and styles
- **Font-aware Analysis**: Uses PyMuPDF to extract detailed font information
- **Duplicate Prevention**: Avoids extracting the same heading multiple times
- **Performance Optimized**: Processes 50-page documents in under 10 seconds
- **Multilingual Support**: Works with various character encodings

## Libraries Used

- **PyMuPDF (fitz)**: PDF text extraction with formatting information
- **pathlib**: Modern path handling
- **json**: Output formatting
- **re**: Regular expression pattern matching

## Technical Details

### Algorithm Flow
1. Open PDF and extract metadata for title
2. Parse each page to get text with font information
3. Calculate average font size across document
4. Apply heading detection patterns and font analysis
5. Score and classify potential headings
6. Sort by page number and filter duplicates
7. Generate JSON output

### Performance Optimizations
- Limits heading extraction to reasonable numbers (≤50)
- Processes only substantial text content
- Uses efficient text parsing with formatting preservation
- Memory-efficient processing for large documents

## Docker Integration

The solution is containerized with:
- **Base**: Python 3.9 slim (AMD64 compatible)
- **Dependencies**: PyMuPDF, pathlib
- **Size**: Optimized for <200MB constraint
- **Runtime**: CPU-only execution

## Build Instructions

```bash
docker build --platform linux/amd64 -f Dockerfile.challenge1a -t challenge1a:latest .
```

## Run Instructions

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1a:latest
```

## Input/Output

**Input**: PDF files in `/app/input/` directory
**Output**: JSON files in `/app/output/` directory (filename.pdf → filename.json)

**JSON Format**:
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Section Title",
      "page": 1
    }
  ]
}
```

## Testing

Tested with sample PDFs including:
- Government forms
- Academic papers
- Technical documents
- Multi-page reports

Achieves high accuracy in heading detection with minimal false positives.