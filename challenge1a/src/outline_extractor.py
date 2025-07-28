"""
Round 1A - Outline Extractor

Extracts structured outline from PDF files using font clustering and layout analysis.
Optimized for competition constraints: CPU-only, <200MB, offline, <10s execution.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

import fitz  # PyMuPDF
import difflib
import numpy as np
try:
    from langdetect import detect, LangDetectError
except ImportError:
    # Fallback if langdetect is not available
    def detect(text):
        return 'en'
    class LangDetectError(Exception):
        pass
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Constants for heading levels
HEADING_LEVELS = ["H1", "H2", "H3"]



class OutlineExtractor:
    """
    Extract hierarchical outline from PDF using font clustering and layout analysis.
    Designed for Adobe Hack Round 1A requirements.
    """
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the outline extractor."""
        self.logger = self._setup_logger(log_level)
        self.scaler = StandardScaler()
        
        # Japanese text patterns for better detection
        self.japanese_patterns = [
            r'[\u3040-\u309F]',  # Hiragana
            r'[\u30A0-\u30FF]',  # Katakana
            r'[\u4E00-\u9FAF]',  # Kanji
        ]
        
        # Common heading patterns for English and Japanese
        self.heading_patterns = {
            'english': [
                r'^(Chapter|Section|Part)\s+\d+',
                r'^\d+\.\s+[A-Z]',
                r'^[A-Z][A-Z\s]+$',
                r'^\d+\.\d+\s+',
                r'^[IVX]+\.\s+',
            ],
            'japanese': [
                r'^第\d+章',
                r'^第\d+節',
                r'^\d+\.\s*',
                r'^[０-９]+\.\s*',
                r'^[一二三四五六七八九十]+\.',
            ]
        }
    
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured outline from PDF file.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Dict[str, Any]: Structured outline in competition format
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Extract document title
            title = self._extract_title(doc)
            
            # Extract text blocks with font information
            text_blocks = self._extract_text_blocks(doc)
            
            # Detect language
            language = self._detect_language(text_blocks)
            
            # Cluster fonts to identify heading levels
            heading_candidates = self._identify_heading_candidates(text_blocks, language)
            
            # Build hierarchical outline
            outline = self._build_outline(heading_candidates)
            
            doc.close()
            
            result = {
                "title": title,
                "outline": outline
            }
            
            self.logger.info(f"Extracted outline with {len(outline)} items from {pdf_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting outline from {pdf_path}: {str(e)}")
            return {"title": "Unknown", "outline": []}
    
    def _extract_title(self, doc: fitz.Document) -> str:
        """Extract document title from metadata or first page."""
        # Try metadata first
        metadata = doc.metadata
        if metadata.get('title'):
            return metadata['title'].strip()
        
        # Try first page - look for largest text or title-like patterns
        if len(doc) > 0:
            page = doc[0]
            blocks = page.get_text("dict")
            
            title_candidates = []
            
            for block in blocks.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        font_size = span.get("size", 0)
                        
                        if (len(text) > 5 and len(text) < 100 and 
                            font_size > 14 and
                            not re.match(r'^\d+$', text)):
                            title_candidates.append((text, font_size, span.get("bbox", [0,0,0,0])[1]))
            
            if title_candidates:
                # Sort by font size (desc) and position (asc)
                title_candidates.sort(key=lambda x: (-x[1], x[2]))
                return title_candidates[0][0]
        
        return "Unknown Document"
    
    def _extract_text_blocks(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Extract text blocks with font and position information, consolidating lines."""
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks.get("blocks", []):
                if "lines" not in block:
                    continue
                
                # Process each line as a unit instead of individual spans
                for line in block["lines"]:
                    line_text = ""
                    line_bbox = None
                    dominant_font_size = 0
                    dominant_font_name = ""
                    dominant_font_flags = 0
                    span_count = 0
                    
                    # Consolidate spans within the same line
                    for span in line.get("spans", []):
                        span_text = span.get("text", "").strip()
                        if not span_text:
                            continue
                            
                        line_text += span_text + " "
                        span_count += 1
                        
                        # Track dominant font characteristics
                        font_size = span.get("size", 12)
                        if font_size > dominant_font_size:
                            dominant_font_size = font_size
                            dominant_font_name = span.get("font", "")
                            dominant_font_flags = span.get("flags", 0)
                        
                        # Expand bounding box
                        span_bbox = span.get("bbox", [0, 0, 0, 0])
                        if line_bbox is None:
                            line_bbox = list(span_bbox)
                        else:
                            line_bbox[0] = min(line_bbox[0], span_bbox[0])  # min x
                            line_bbox[1] = min(line_bbox[1], span_bbox[1])  # min y
                            line_bbox[2] = max(line_bbox[2], span_bbox[2])  # max x
                            line_bbox[3] = max(line_bbox[3], span_bbox[3])  # max y
                    
                    line_text = line_text.strip()
                    
                    # Skip empty lines or very short text
                    if len(line_text) < 3:
                        continue
                    
                    # Skip lines that are likely page numbers, headers, footers
                    if (re.match(r'^\d+$', line_text) or
                        len(line_text) > 300 or  # Very long lines are likely body text
                        line_text.lower() in ['page', 'contents', 'index', 'references', 'bibliography']):
                        continue
                    
                    if line_bbox is None:
                        line_bbox = [0, 0, 0, 0]
                    
                    text_block = {
                        'text': line_text,
                        'page': page_num + 1,
                        'font_size': dominant_font_size,
                        'font_name': dominant_font_name,
                        'font_flags': dominant_font_flags,
                        'bbox': line_bbox,
                        'x': line_bbox[0],
                        'y': line_bbox[1],
                        'width': line_bbox[2] - line_bbox[0],
                        'height': line_bbox[3] - line_bbox[1],
                        'span_count': span_count
                    }
                    
                    text_blocks.append(text_block)
        
        return text_blocks
    
    def _detect_language(self, text_blocks: List[Dict[str, Any]]) -> str:
        """Detect document language (English or Japanese)."""
        # Combine text from first few pages for detection
        sample_text = " ".join([
            block['text'] for block in text_blocks[:100]
            if len(block['text']) > 5
        ])
        
        # Check for Japanese characters first
        japanese_chars = sum(1 for pattern in self.japanese_patterns 
                           if re.search(pattern, sample_text))
        
        if japanese_chars > 10:
            return 'japanese'
        
        # Use langdetect for other languages
        try:
            detected = detect(sample_text)
            return 'japanese' if detected == 'ja' else 'english'
        except LangDetectError:
            return 'english'  # Default to English
    
    def _identify_heading_candidates(self, text_blocks: List[Dict[str, Any]],
                                   language: str) -> List[Dict[str, Any]]:
        """Identify potential headings using improved font analysis and pattern matching."""
        if len(text_blocks) < 10:
            return []
        
        # Feature extraction for clustering
        features = []
        for block in text_blocks:
            is_bold = 1 if block['font_flags'] & 2**4 else 0
            is_all_caps = 1 if block['text'].isupper() and len(block['text']) > 5 else 0
            features.append([block['font_size'], is_bold, block['x'], is_all_caps])
        
        if not features:
            return []

        features_scaled = self.scaler.fit_transform(features)

        # Determine number of clusters (k)
        unique_font_sizes = np.unique([f[0] for f in features])
        k = min(len(unique_font_sizes), 8)
        k = max(k, 3) # Ensure at least 3 clusters

        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(features_scaled)

        # Analyze clusters to find heading clusters
        cluster_info = defaultdict(lambda: {'sizes': [], 'count': 0})
        for i, label in enumerate(labels):
            cluster_info[label]['sizes'].append(text_blocks[i]['font_size'])
            cluster_info[label]['count'] += 1

        # Calculate average font size for each cluster
        avg_cluster_sizes = {
            label: np.mean(info['sizes']) for label, info in cluster_info.items()
        }

        # Sort clusters by average font size (descending)
        sorted_clusters = sorted(avg_cluster_sizes.items(), key=lambda item: item[1], reverse=True)

        # Identify top N clusters as headings (up to 3 levels)
        heading_cluster_labels = [label for label, size in sorted_clusters[:len(HEADING_LEVELS)]]
        
        # Map cluster labels to H1, H2, H3
        level_map = {label: HEADING_LEVELS[i] for i, (label, size) in enumerate(sorted_clusters[:len(HEADING_LEVELS)])}

        # Filter for heading candidates from the identified clusters
        heading_candidates = []
        for i, block in enumerate(text_blocks):
            label = labels[i]
            if label in heading_cluster_labels:
                # Filter out paragraph-like text
                text = block['text']
                if len(text) > 150 or text.count(' ') > 20 or len(text) < 4:
                    continue
                
                candidate = block.copy()
                candidate['level'] = level_map[label]
                heading_candidates.append(candidate)

        return heading_candidates
    
    def _build_outline(self, heading_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build hierarchical outline from heading candidates with improved logic."""
        if not heading_candidates:
            return []
        
        # Sort candidates by page and position
        heading_candidates.sort(key=lambda x: (x['page'], x['y']))

        outline = []
        for candidate in heading_candidates:
            # Clean up text more thoroughly
            text = candidate['text'].strip()
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = re.sub(r'^[\d\.\-\s]+', '', text).strip()  # Remove leading numbers/dots
            text = re.sub(r'[\.\-\s]+$', '', text).strip()  # Remove trailing punctuation
            
            # Skip if text becomes too short after cleaning
            if len(text) < 3:
                continue
            
            # Capitalize first letter if not already
            if text and text[0].islower():
                text = text[0].upper() + text[1:]
            
            outline_item = {
                "level": candidate['level'],
                "text": text,
                "page": candidate['page']
            }
            
            outline.append(outline_item)
        
        # Remove duplicates and very similar items
        unique_outline = []
        seen_texts = set()
        
        for item in outline:
            text_key = item['text'].lower().strip()
            
            # Check for very similar existing items
            is_similar = False
            for seen_text in seen_texts:
                similarity = difflib.SequenceMatcher(None, text_key, seen_text).ratio()
                if similarity > 0.85:
                    is_similar = True
                    break
            
            if not is_similar:
                seen_texts.add(text_key)
                unique_outline.append(item)
        
        return unique_outline
    
    def save_outline(self, outline_data: Dict[str, Any], output_path: str) -> bool:
        """Save outline to JSON file."""
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(outline_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Outline saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving outline to {output_path}: {str(e)}")
            return False
    
    def process_pdf(self, input_path: str, output_path: str) -> bool:
        """Process PDF and save outline (main entry point)."""
        outline_data = self.extract_outline(input_path)
        return self.save_outline(outline_data, output_path)


def main():
    """CLI entry point for testing."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python outline_extractor.py <input_pdf> <output_json>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    extractor = OutlineExtractor()
    success = extractor.process_pdf(input_path, output_path)
    
    if success:
        print(f"Outline extracted successfully: {output_path}")
    else:
        print("Failed to extract outline")
        sys.exit(1)


if __name__ == "__main__":
    main()