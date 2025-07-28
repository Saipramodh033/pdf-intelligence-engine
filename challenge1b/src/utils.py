"""
Utility Functions for PDF Processing - Challenge 1B

Optimized utilities for Adobe Hack competition constraints:
- CPU-only processing
- Lightweight operations
- Fast execution (<10s for 50-page PDFs)
- Offline functionality
"""

import json
import logging
import os
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

import fitz  # PyMuPDF
import numpy as np

try:
    from langdetect import detect, LangDetectError
except ImportError:
    def detect(text): return 'en'
    class LangDetectError(Exception): pass


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger("pdf_processor")
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def validate_pdf_file(file_path: str) -> bool:
    if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
        return False
    try:
        with open(file_path, 'rb') as f:
            if not f.read(8).startswith(b'%PDF'):
                return False
        doc = fitz.open(file_path)
        valid = len(doc) > 0
        doc.close()
        return valid
    except Exception:
        return False


def get_pdf_info(file_path: str) -> Dict[str, Any]:
    info = {
        'path': file_path, 'exists': False, 'valid_pdf': False,
        'size_bytes': 0, 'size_mb': 0.0, 'page_count': 0,
        'title': '', 'author': '', 'subject': '', 'creator': '',
        'producer': '', 'creation_date': '', 'modification_date': '',
        'encrypted': False, 'has_outline': False, 'language': 'unknown'
    }

    try:
        if not os.path.exists(file_path):
            return info

        info['exists'] = True
        stat = os.stat(file_path)
        info['size_bytes'] = stat.st_size
        info['size_mb'] = round(stat.st_size / (1024 * 1024), 2)

        if validate_pdf_file(file_path):
            info['valid_pdf'] = True
            doc = fitz.open(file_path)
            info['page_count'] = len(doc)
            info['encrypted'] = doc.needs_pass
            info['has_outline'] = bool(doc.get_toc())
            meta = doc.metadata
            info['title'] = meta.get('title', '').strip()
            info['author'] = meta.get('author', '').strip()
            info['subject'] = meta.get('subject', '').strip()
            info['creator'] = meta.get('creator', '').strip()
            info['producer'] = meta.get('producer', '').strip()
            info['creation_date'] = meta.get('creationDate', '').strip()
            info['modification_date'] = meta.get('modDate', '').strip()

            try:
                first_text = doc[0].get_text()[:1000]
                info['language'] = detect_language_fast(first_text)
            except Exception:
                pass
            doc.close()

    except Exception as e:
        logging.warning(f"Error getting PDF info for {file_path}: {str(e)}")
    return info


def get_file_info(file_path: str) -> Dict[str, Any]:
    return get_pdf_info(file_path)


def detect_language_fast(text: str) -> str:
    if not text or len(text) < 10:
        return 'unknown'
    jp_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    total_chars = len(re.findall(r'[^\s\d\W]', text))
    if total_chars == 0:
        return 'unknown'
    if jp_chars / total_chars > 0.1:
        return 'japanese'
    try:
        detected = detect(text)
        return 'japanese' if detected == 'ja' else 'english'
    except LangDetectError:
        logging.warning("Language detection failed, defaulting to 'english'.")
        return 'english'


def find_pdf_files(directory: str, recursive: bool = True, max_files: int = 100) -> List[str]:
    pdf_files = []
    try:
        path = Path(directory)
        if not path.exists():
            logging.warning(f"Directory does not exist: {directory}")
            return []
        pattern = "**/*.pdf" if recursive else "*.pdf"
        for file in path.glob(pattern):
            if len(pdf_files) >= max_files:
                break
            if file.is_file() and validate_pdf_file(str(file)):
                pdf_files.append(str(file))
        logging.info(f"Found {len(pdf_files)} PDF files in {directory}")
    except Exception as e:
        logging.error(f"Error finding PDFs in {directory}: {str(e)}")
    return sorted(pdf_files)


def ensure_output_directory(output_path: str) -> bool:
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create output directory: {str(e)}")
        return False


def save_json_fast(data: Any, output_path: str, indent: int = 2) -> bool:
    try:
        if not ensure_output_directory(output_path):
            return False
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {output_path}: {str(e)}")
        return False


def load_json_fast(file_path: str) -> Optional[Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON from {file_path}: {str(e)}")
        return None


def extract_text_blocks_fast(doc: fitz.Document, max_pages: int = 50) -> List[Dict[str, Any]]:
    blocks = []
    for i in range(min(len(doc), max_pages)):
        try:
            for block in doc[i].get_text("dict").get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if len(text) < 2:
                            continue
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        blocks.append({
                            'text': text,
                            'page': i + 1,
                            'font_size': span.get("size", 12),
                            'font_name': span.get("font", ""),
                            'font_flags': span.get("flags", 0),
                            'bbox': bbox,
                            'x': bbox[0],
                            'y': bbox[1]
                        })
        except Exception as e:
            logging.warning(f"Error processing page {i + 1}: {str(e)}")
    return blocks


def calculate_file_hash_fast(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> Optional[str]:
    try:
        hasher = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing {file_path}: {str(e)}")
        return None


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {units[i]}"


def create_output_filename(input_path: str, suffix: str = "", extension: str = ".json") -> str:
    return f"{Path(input_path).stem}{suffix}{extension}"


def normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)


def extract_sentences_fast(text: str, max_sentences: int = 1000) -> List[str]:
    sentences = re.split(r'[.!?。！？]\s+', text)
    return [
        normalize_text(s) for s in sentences[:max_sentences]
        if 10 < len(s) < 500
    ]


def cluster_font_sizes(font_sizes: List[float], max_clusters: int = 5) -> Dict[float, int]:
    if not font_sizes:
        return {}
    unique = sorted(set(font_sizes), reverse=True)
    clusters = {}
    for i, size in enumerate(unique):
        clusters[size] = min(i, max_clusters - 1)
    return clusters


def validate_competition_constraints(file_path: str) -> Dict[str, Any]:
    result = {
        'valid': True, 'errors': [], 'warnings': [],
        'file_size_mb': 0, 'page_count': 0
    }
    if not validate_pdf_file(file_path):
        result['valid'] = False
        result['errors'].append("Invalid or missing PDF file")
        return result
    info = get_pdf_info(file_path)
    result['file_size_mb'] = info['size_mb']
    result['page_count'] = info['page_count']
    if info['page_count'] > 50:
        result['valid'] = False
        result['errors'].append("PDF has too many pages (max 50)")
    if info['size_mb'] > 100:
        result['warnings'].append(f"File size is large: {info['size_mb']} MB")
    if info['encrypted']:
        result['valid'] = False
        result['errors'].append("Encrypted PDF not supported")
    return result


def print_processing_stats(stats: Dict[str, Any]) -> None:
    print("\n" + "="*50)
    print("PROCESSING STATISTICS")
    print("="*50)
    if 'execution_time' in stats:
        print(f"Execution time: {stats['execution_time']}s")
    if 'file_info' in stats:
        info = stats['file_info']
        print(f"File size: {format_file_size(info.get('size_bytes', 0))}")
        print(f"Pages: {info.get('page_count', 0)}")
        print(f"Language: {info.get('language', 'unknown')}")
    if 'task_sections' in stats:
        print(f"Task sections found: {stats['task_sections']}")
    if 'memory_usage' in stats:
        print(f"Peak memory: {format_file_size(stats['memory_usage'])}")
    print("="*50)


def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
    patterns = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
        r'\b(?:data|machine|learning|analysis|model|system|process|method)\s+\w+\b',
    ]
    phrases = []
    for p in patterns:
        phrases += re.findall(p, text, re.IGNORECASE)
    return list(set(phrases))[:max_phrases]