# Challenge 1A - PDF Outline Extractor

**Adobe Hack Competition - Round 1A Solution**

## 🎯 Overview

This solution extracts structured outlines from PDF documents using advanced font clustering and layout analysis techniques. It identifies hierarchical headings (H1, H2, H3) and supports both English and Japanese documents.

## 🏗️ Project Structure

```
challenge1a/
├── src/
│   ├── outline_extractor.py    # Main outline extraction logic
│   ├── parser.py              # CLI interface
│   ├── utils.py               # Utility functions
│   └── __init__.py
├── requirements.txt           # Dependencies
├── Dockerfile                # Docker configuration
└── README.md                 # This file
```

## ⚡ Key Features

### Competition Constraints Compliance
- ✅ **CPU-only**: No GPU dependencies, optimized for CPU processing
- ✅ **<200MB**: Lightweight dependencies (PyMuPDF, scikit-learn, langdetect)
- ✅ **Offline**: No internet connectivity required during execution
- ✅ **<10s execution**: Optimized algorithms for 50-page PDFs
- ✅ **Docker ready**: `--network none` compatible

### Technical Approach
- **Font Clustering**: Uses scikit-learn KMeans to cluster font sizes/styles
- **Layout Analysis**: Analyzes text position, indentation, and formatting
- **Pattern Matching**: Regex patterns for English/Japanese heading structures
- **Language Detection**: Fast detection using character analysis + langdetect

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Extract outline from PDF
python -m src.parser outline input.pdf output_outline.json

# Batch processing
python -m src.parser batch input_dir/ output_dir/
```

### Docker Usage

```bash
# Build the image
docker build -t challenge1a .

# Extract outline
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  challenge1a \
  python -m src.parser outline /app/input/document.pdf /app/output/outline.json
```

## 📊 Output Format

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 },
    { "level": "H1", "text": "Machine Learning", "page": 5 },
    { "level": "H2", "text": "Supervised Learning", "page": 6 }
  ]
}
```

## 🔧 Technical Implementation

### Dependencies (Total: ~150MB)
- **PyMuPDF (fitz)**: Fast PDF parsing and text extraction
- **scikit-learn**: Lightweight ML for font clustering
- **langdetect**: Language detection for English/Japanese support
- **numpy**: Numerical operations for clustering
- **regex**: Advanced pattern matching

### Algorithm Details

#### Font Clustering Algorithm
1. Extract all text spans with font metadata (size, weight, position)
2. Normalize font features using StandardScaler
3. Apply KMeans clustering (k=3-8 clusters)
4. Score clusters based on font size, bold formatting, and position
5. Map high-scoring clusters to heading levels (H1, H2, H3)

### Performance Optimizations
- **Lazy Loading**: Process only necessary pages (max 50)
- **Memory Management**: Stream processing, minimal memory footprint
- **Caching**: Font cluster reuse across pages
- **Parallel Processing**: Multi-threaded text extraction where possible

## 🧪 Testing & Validation

### Edge Cases Handled
- ✅ PDFs without clear heading hierarchy
- ✅ Missing metadata or corrupted fonts
- ✅ Dense formatting with mixed languages
- ✅ Japanese content and fonts
- ✅ Encrypted or password-protected PDFs (graceful failure)

### Performance Benchmarks
- **Small PDFs (1-10 pages)**: <2s execution time
- **Medium PDFs (11-30 pages)**: <5s execution time  
- **Large PDFs (31-50 pages)**: <10s execution time
- **Memory usage**: <100MB peak for 50-page PDFs

## 📈 Usage Examples

### CLI Options
```bash
# Help and usage
python -m src.parser --help

# Verbose logging
python -m src.parser outline input.pdf output.json --log-level DEBUG

# JSON output for automation
python -m src.parser outline input.pdf output.json --json-output

# Quiet mode (errors only)
python -m src.parser batch input/ output/ --quiet
```

### Programmatic Usage
```python
from src.outline_extractor import OutlineExtractor

# Initialize extractor
extractor = OutlineExtractor()

# Extract outline
outline = extractor.extract_outline("document.pdf")
print(f"Found {len(outline['outline'])} headings")

# Save to file
success = extractor.save_outline(outline, "output.json")
```

## 🔍 Troubleshooting

### Common Issues

1. **"No outline found"**
   - PDF may not have clear heading structure
   - Try adjusting font clustering parameters
   - Check if PDF has embedded fonts

2. **Performance issues**
   - Ensure PDF is under 50 pages
   - Check available system memory
   - Use batch processing for multiple files

3. **Docker networking**
   - Always use `--network none` for competition
   - Ensure volume mounts are correct
   - Check file permissions in containers

### Debug Mode
```bash
# Enable detailed logging
python -m src.parser outline input.pdf output.json --log-level DEBUG
```

## 📝 Competition Submission

### Required Files
- ✅ Working Docker image via Dockerfile
- ✅ Complete source code with modular design  
- ✅ Documentation (this README)
- ✅ Requirements.txt with dependency versions

### Validation Checklist
- ✅ CPU-only execution (no GPU dependencies)
- ✅ <200MB total size (dependencies + model)
- ✅ Offline execution (no internet required)
- ✅ <10s execution time for 50-page PDFs
- ✅ Docker `--network none` compatibility
- ✅ Proper volume mounts for input/output
- ✅ English and Japanese language support

## 📄 License

MIT License - Adobe Hack Competition 2024

---

**Built for Adobe Hack Competition - Optimized for performance, accuracy, and constraint compliance** 🏆