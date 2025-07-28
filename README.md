# Adobe Hack - PDF Processing Challenges

**Separated Challenge Solutions for Adobe Hack Competition**

## 🎯 Overview

This repository contains separated solutions for Adobe Hack PDF processing challenges:

- **Challenge 1A**: PDF Outline Extractor
- **Challenge 1B**: Task Section Extractor

Each challenge is now in its own independent folder with complete code, documentation, and Docker configuration.

## 🏗️ Project Structure

```
adobe_hack/
├── challenge1a/                    # Challenge 1A - Outline Extractor
│   ├── src/
│   │   ├── outline_extractor.py    # Main outline extraction logic
│   │   ├── parser.py              # CLI interface
│   │   ├── utils.py               # Utility functions
│   │   └── __init__.py
│   ├── requirements.txt           # Dependencies
│   ├── Dockerfile                # Docker configuration
│   └── README.md                 # Challenge 1A documentation
│
├── challenge1b/                    # Challenge 1B - Task Section Extractor
│   ├── src/
│   │   ├── persona_extractor.py   # Main task section extraction logic
│   │   ├── parser.py              # CLI interface
│   │   ├── utils.py               # Utility functions
│   │   └── __init__.py
│   ├── requirements.txt           # Dependencies
│   ├── Dockerfile                # Docker configuration
│   └── README.md                 # Challenge 1B documentation
│
├── input/                         # Sample input PDFs (shared)
├── output/                        # Output directory (shared)
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🚀 Quick Start

### Challenge 1A - Outline Extractor

Extract structured outlines from PDF documents:

```bash
# Navigate to challenge1a
cd challenge1a

# Install dependencies
pip install -r requirements.txt

# Extract outline
python -m src.parser outline ../input/document.pdf ../output/outline.json

# Docker usage
docker build -t challenge1a .
docker run --rm \
  -v $(pwd)/../input:/app/input \
  -v $(pwd)/../output:/app/output \
  --network none \
  challenge1a \
  python -m src.parser outline /app/input/document.pdf /app/output/outline.json
```

### Challenge 1B - Task Section Extractor

Extract document sections relevant to persona tasks:

```bash
# Navigate to challenge1b
cd challenge1b

# Install dependencies
pip install -r requirements.txt

# Extract task sections
python -m src.parser persona ../input/document.pdf ../output/task_sections.json

# Docker usage
docker build -t challenge1b .
docker run --rm \
  -v $(pwd)/../input:/app/input \
  -v $(pwd)/../output:/app/output \
  --network none \
  challenge1b \
  python -m src.parser persona /app/input/document.pdf /app/output/task_sections.json
```

## 📊 Output Formats

### Challenge 1A - Outline Format
```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

### Challenge 1B - Task Section Format
```json
{
  "task_sections": [
    {
      "text": "The analysis involves statistical examination...",
      "page": 5,
      "relevant_tasks": ["data_analysis", "optimization"],
      "relevance_scores": {
        "data_analysis": 0.85,
        "optimization": 0.3
      },
      "section_type": "methodology",
      "length": 245,
      "context_available": true
    }
  ]
}
```

## ⚡ Key Features

### Competition Constraints Compliance
Both challenges are optimized for Adobe Hack competition requirements:

- ✅ **CPU-only**: No GPU dependencies
- ✅ **<200MB**: Lightweight dependencies
- ✅ **Offline**: No internet connectivity required
- ✅ **<10s execution**: Fast processing for 50-page PDFs
- ✅ **Docker ready**: `--network none` compatible

### Technical Highlights

#### Challenge 1A (Outline Extractor)
- Font clustering using scikit-learn KMeans
- Layout analysis for heading detection
- English/Japanese language support
- Hierarchical outline generation (H1, H2, H3)

#### Challenge 1B (Task Section Extractor)
- 8 persona task types coverage
- Multi-criteria relevance scoring
- Lightweight Naive Bayes classification
- Context-aware section extraction

## 🧪 Testing

Each challenge can be tested independently:

```bash
# Test Challenge 1A
cd challenge1a
python -m src.parser outline ../input/sample.pdf ../output/test_outline.json

# Test Challenge 1B
cd challenge1b
python -m src.parser persona ../input/sample.pdf ../output/test_sections.json
```

## 📝 Documentation

Detailed documentation is available in each challenge folder:

- [`challenge1a/README.md`](challenge1a/README.md) - Complete Challenge 1A documentation
- [`challenge1b/README.md`](challenge1b/README.md) - Complete Challenge 1B documentation

## 🏆 Competition Advantages

### 1. Modular Design
- Clean separation of concerns
- Independent deployment capability
- Easy maintenance and updates

### 2. Optimized Performance
- Sub-10s execution for 50-page PDFs
- Memory-efficient processing
- Lightweight ML models

### 3. Comprehensive Coverage
- **Challenge 1A**: Robust outline extraction with font analysis
- **Challenge 1B**: Complete persona task coverage (8 task types)

### 4. Production Ready
- Docker containerization
- Comprehensive error handling
- Extensive logging and debugging

## 🔧 Development

### Prerequisites
- Python 3.10+
- Docker (optional)
- PDF files for testing

### Setup
```bash
# Clone repository
git clone <repository-url>
cd adobe_hack

# Set up Challenge 1A
cd challenge1a
pip install -r requirements.txt

# Set up Challenge 1B
cd ../challenge1b
pip install -r requirements.txt
```

## 📄 License

MIT License - Adobe Hack Competition 2024

## 🤝 Contributing

This is a competition submission. For questions or issues, please refer to the individual challenge documentation.

---

**Built for Adobe Hack Competition - Two independent, optimized solutions for PDF processing challenges** 🏆