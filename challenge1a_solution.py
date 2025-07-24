#!/usr/bin/env python3
"""
Challenge 1A: PDF Outline Extraction Solution
Extracts structured outlines (title, headings H1/H2/H3) from PDF documents
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF


class PDFOutlineExtractor:
    def __init__(self):
        self.heading_patterns = [
            # Chapter/Section patterns
            r'^(Chapter|CHAPTER)\s+\d+[:\-\s]*(.+)',
            r'^(\d+\.)\s*([A-Z][A-Za-z\s]+)',
            r'^(\d+\.\d+)\s*([A-Z][A-Za-z\s]+)',
            r'^(\d+\.\d+\.\d+)\s*([A-Z][A-Za-z\s]+)',
            
            # Roman numeral patterns
            r'^([IVX]+\.)\s*([A-Z][A-Za-z\s]+)',
            
            # Alphabetical patterns
            r'^([A-Z]\.)\s*([A-Z][A-Za-z\s]+)',
            
            # Bold/Uppercase patterns (will be checked via formatting)
            r'^([A-Z][A-Z\s]{3,})',
            
            # Introduction, Conclusion patterns
            r'^(Introduction|INTRODUCTION|Conclusion|CONCLUSION|Abstract|ABSTRACT|Summary|SUMMARY)$',
            
            # Generic heading patterns
            r'^([A-Z][A-Za-z\s]{5,})(?:\s*$)',
        ]
    
    def extract_title_from_text(self, text: str) -> Optional[str]:
        """Extract title from PDF text content"""
        lines = text.split('\n')
        
        # Clean lines and remove empty ones
        clean_lines = [line.strip() for line in lines if line.strip()]
        
        if not clean_lines:
            return None
        
        # Look for title in first few lines
        for i, line in enumerate(clean_lines[:10]):
            # Skip very short lines (likely page numbers, etc.)
            if len(line) < 5:
                continue
            
            # Skip lines that look like headers/footers
            if re.match(r'^\d+$|^Page \d+|^\d+/\d+$', line):
                continue
            
            # Check if line looks like a title
            if (len(line) > 10 and 
                not line.endswith('.') and 
                not re.match(r'^\d+\.', line) and
                len(line.split()) >= 2):
                return line.strip()
        
        # Fallback to first substantial line
        for line in clean_lines:
            if len(line) > 10:
                return line.strip()
        
        return clean_lines[0] if clean_lines else "Untitled Document"
    
    def get_font_info(self, page, text_instance) -> Tuple[float, str, int]:
        """Extract font size, name, and flags from text instance"""
        try:
            font_size = text_instance['size']
            font_name = text_instance.get('font', '')
            flags = text_instance.get('flags', 0)
            return font_size, font_name, flags
        except:
            return 12.0, '', 0
    
    def is_bold(self, flags: int) -> bool:
        """Check if text is bold based on font flags"""
        return bool(flags & 2**4)  # Bold flag
    
    def classify_heading_level(self, text: str, font_size: float, is_bold: bool, 
                             avg_font_size: float) -> Optional[str]:
        """Classify text as H1, H2, or H3 based on various criteria"""
        text = text.strip()
        
        # Skip very short or long text
        if len(text) < 3 or len(text) > 200:
            return None
        
        # Skip text that ends with punctuation (likely paragraph text)
        if text.endswith(('.', '!', '?', ';', ',')):
            return None
        
        # Check against heading patterns
        heading_score = 0
        pattern_level = None
        
        for pattern in self.heading_patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                heading_score += 2
                # Determine level based on pattern
                if 'chapter' in pattern.lower() or pattern.count(r'\d+\.') == 1:
                    pattern_level = 'H1'
                elif pattern.count(r'\d+\.') == 2:
                    pattern_level = 'H2'
                elif pattern.count(r'\d+\.') == 3:
                    pattern_level = 'H3'
                break
        
        # Font size scoring
        font_score = 0
        if font_size > avg_font_size * 1.5:
            font_score += 3
        elif font_size > avg_font_size * 1.2:
            font_score += 2
        elif font_size > avg_font_size:
            font_score += 1
        
        # Bold text scoring
        if is_bold:
            heading_score += 1
        
        # Uppercase scoring
        if text.isupper() and len(text) > 5:
            heading_score += 1
        
        # Title case scoring
        if text.istitle():
            heading_score += 1
        
        total_score = heading_score + font_score
        
        # Classification logic
        if total_score >= 4 or (pattern_level == 'H1'):
            return 'H1'
        elif total_score >= 3 or (pattern_level == 'H2'):
            return 'H2'
        elif total_score >= 2 or (pattern_level == 'H3'):
            return 'H3'
        
        return None
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract outline from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            
            # Try to extract title from metadata first
            title = doc.metadata.get('title', '').strip()
            
            # Collect all text with formatting info
            all_text = []
            all_font_sizes = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get text with formatting
                text_dict = page.get_text("dict")
                
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text_content = span["text"].strip()
                                if text_content:
                                    font_size, font_name, flags = self.get_font_info(page, span)
                                    all_text.append((text_content, font_size, flags, page_num + 1))
                                    all_font_sizes.append(font_size)
            
            # Calculate average font size
            avg_font_size = sum(all_font_sizes) / len(all_font_sizes) if all_font_sizes else 12.0
            
            # If no title from metadata, extract from content
            if not title:
                full_text = ' '.join([t[0] for t in all_text[:100]])  # First 100 text segments
                title = self.extract_title_from_text(full_text) or "Untitled Document"
            
            # Extract headings
            outline = []
            seen_headings = set()
            
            for text_content, font_size, flags, page_num in all_text:
                is_bold_text = self.is_bold(flags)
                heading_level = self.classify_heading_level(text_content, font_size, is_bold_text, avg_font_size)
                
                if heading_level:
                    # Clean the heading text
                    clean_text = re.sub(r'^[\d\.\s\-IVX]+', '', text_content).strip()
                    if not clean_text:
                        clean_text = text_content.strip()
                    
                    # Avoid duplicates
                    heading_key = (clean_text.lower(), page_num)
                    if heading_key not in seen_headings and len(clean_text) >= 3:
                        outline.append({
                            "level": heading_level,
                            "text": clean_text,
                            "page": page_num
                        })
                        seen_headings.add(heading_key)
            
            doc.close()
            
            # Sort by page number and remove excessive headings
            outline.sort(key=lambda x: (x['page'], x['level']))
            
            # Limit to reasonable number of headings
            outline = outline[:50]
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return {
                "title": f"Error processing {os.path.basename(pdf_path)}",
                "outline": []
            }


def process_pdfs():
    """Process all PDFs in input directory"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize extractor
    extractor = PDFOutlineExtractor()
    
    # Process all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        
        # Extract outline
        result = extractor.extract_outline(str(pdf_file))
        
        # Save result
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Completed {pdf_file.name} -> {output_file.name}")


if __name__ == "__main__":
    print("Starting PDF outline extraction...")
    process_pdfs()
    print("PDF outline extraction completed!")