# Challenge 1B - Task Section Extractor

**Adobe Hack Competition - Round 1B Solution**

## 🎯 Overview

This solution extracts document sections relevant to persona tasks from PDF documents. It identifies sections for data analysis, system design, implementation, troubleshooting, optimization, documentation, planning, and collaboration tasks using advanced NLP and pattern matching techniques.

## 🏗️ Project Structure

```
challenge1b/
├── src/
│   ├── persona_extractor.py   # Main task section extraction logic
│   ├── parser.py             # CLI interface
│   ├── utils.py              # Utility functions
│   └── __init__.py
├── requirements.txt          # Dependencies
├── Dockerfile               # Docker configuration
└── README.md                # This file
```

## ⚡ Key Features

### Competition Constraints Compliance
- ✅ **CPU-only**: No GPU dependencies, optimized for CPU processing
- ✅ **<200MB**: Lightweight dependencies (PyMuPDF, scikit-learn, langdetect)
- ✅ **Offline**: No internet connectivity required during execution
- ✅ **<10s execution**: Optimized algorithms for 50-page PDFs
- ✅ **Docker ready**: `--network none` compatible

### Technical Approach
- **Task Relevance Scoring**: Multi-criteria scoring for 8 persona task types
- **Lightweight ML**: Naive Bayes classifier for section categorization (<1MB model)
- **Context Analysis**: Paragraph-level context extraction for better accuracy
- **Section Type Classification**: Methodology, requirements, examples, best practices, etc.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Extract task sections from PDF
python -m src.parser persona input.pdf output_task_sections.json

# Batch processing
python -m src.parser batch input_dir/ output_dir/
```

### Docker Usage

```bash
# Build the image
docker build -t challenge1b .

# Extract task sections
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  challenge1b \
  python -m src.parser persona /app/input/document.pdf /app/output/task_sections.json
```

## 📊 Output Format

```json
{
  "task_sections": [
    {
      "text": "The analysis involves statistical examination of customer behavior patterns...",
      "page": 5,
      "relevant_tasks": ["data_analysis", "optimization"],
      "relevance_scores": {
        "data_analysis": 0.85,
        "optimization": 0.3
      },
      "section_type": "methodology",
      "length": 245,
      "context_available": true
    },
    {
      "text": "System architecture should follow microservices design patterns...",
      "page": 12,
      "relevant_tasks": ["system_design", "implementation"],
      "relevance_scores": {
        "system_design": 0.9,
        "implementation": 0.4
      },
      "section_type": "best_practices",
      "length": 189,
      "context_available": false
    }
  ]
}
```

## 🔧 Technical Implementation

### Dependencies (Total: ~150MB)
- **PyMuPDF (fitz)**: Fast PDF parsing and text extraction
- **scikit-learn**: Lightweight ML for text classification
- **langdetect**: Language detection for English/Japanese support
- **numpy**: Numerical operations for scoring
- **regex**: Advanced pattern matching

### Persona Task Types

The system identifies sections relevant to 8 persona task types:

1. **Data Analysis**: Statistical analysis, metrics, trends, patterns
2. **System Design**: Architecture, components, frameworks, scalability
3. **Implementation**: Development, coding, deployment, testing
4. **Troubleshooting**: Debugging, error handling, problem resolution
5. **Optimization**: Performance tuning, efficiency improvements
6. **Documentation**: Guides, manuals, instructions, references
7. **Planning**: Roadmaps, requirements, timelines, objectives
8. **Collaboration**: Team coordination, communication, stakeholder engagement

### Algorithm Details

#### Task Section Extraction Pipeline
1. **Text Preprocessing**: Paragraph segmentation with context windows
2. **Task Relevance Scoring**: Multi-criteria scoring against 8 persona task types
3. **Section Classification**: Pattern matching for methodology, requirements, examples, etc.
4. **ML Classification**: Naive Bayes for content categorization
5. **Post-processing**: Deduplication and relevance filtering

### Performance Optimizations
- **Lazy Loading**: Process only necessary pages (max 50)
- **Memory Management**: Stream processing, minimal memory footprint
- **Context Windows**: Efficient paragraph-level processing
- **Relevance Filtering**: Only sections above threshold (0.3) are included

## 🧪 Testing & Validation

### Edge Cases Handled
- ✅ PDFs without clear task-relevant content
- ✅ Multiple task-relevant sections per page
- ✅ Mixed languages (English/Japanese)
- ✅ Dense formatting with overlapping content
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
python -m src.parser persona input.pdf output.json --log-level DEBUG

# JSON output for automation
python -m src.parser persona input.pdf output.json --json-output

# Quiet mode (errors only)
python -m src.parser batch input/ output/ --quiet
```

### Programmatic Usage
```python
from src.persona_extractor import PersonaTaskSectionExtractor

# Initialize extractor
extractor = PersonaTaskSectionExtractor()

# Extract task sections
sections = extractor.extract_task_relevant_sections("document.pdf")
print(f"Found {len(sections['task_sections'])} task sections")

# Save to file
success = extractor.save_task_sections(sections, "output.json")
```

## 🔍 Troubleshooting

### Common Issues

1. **"No task sections detected"**
   - Document may not contain task-relevant content
   - Verify language detection is correct
   - Check task relevance scoring thresholds

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
python -m src.parser persona input.pdf output.json --log-level DEBUG
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
- ✅ Task section extraction functionality
- ✅ English and Japanese language support

## 🏆 Competitive Advantages

### 1. Comprehensive Task Coverage
- Covers all 8 major persona task types
- Multi-criteria relevance scoring for accuracy

### 2. Lightweight ML Approach
- **No large transformers**: Custom patterns + lightweight scikit-learn
- **Statistical NLP**: TF-IDF + Naive Bayes for task classification
- **Rule-based extraction**: Optimized patterns for task identification

### 3. Context-Aware Processing
- Paragraph-level context windows
- Section type classification for better understanding
- Deduplication and relevance filtering

## 📄 License

MIT License - Adobe Hack Competition 2024

---

**Built for Adobe Hack Competition - Optimized for performance, accuracy, and constraint compliance** 🏆