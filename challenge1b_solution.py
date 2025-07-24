#!/usr/bin/env python3
"""
Challenge 1B: Persona-Driven Document Intelligence Solution
Extracts and ranks relevant sections from document collections based on persona and job requirements
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import fitz  # PyMuPDF
from collections import defaultdict
import math


class PersonaDocumentAnalyzer:
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF, organized by page number"""
        try:
            doc = fitz.open(pdf_path)
            pages_text = {}
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages_text[page_num + 1] = text
            
            doc.close()
            return pages_text
            
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {str(e)}")
            return {}
    
    def extract_sections_from_text(self, text: str, page_num: int) -> List[Tuple[str, str, int]]:
        """Extract sections from text content"""
        sections = []
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_section_title = None
        current_section_content = []
        
        for paragraph in paragraphs:
            lines = paragraph.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a potential section heading
                if self.is_section_heading(line):
                    # Save previous section if exists
                    if current_section_title and current_section_content:
                        content = ' '.join(current_section_content)
                        if len(content) > 50:  # Only include substantial content
                            sections.append((current_section_title, content, page_num))
                    
                    # Start new section
                    current_section_title = line
                    current_section_content = []
                else:
                    # Add to current section content
                    if current_section_title:
                        current_section_content.append(line)
        
        # Add final section
        if current_section_title and current_section_content:
            content = ' '.join(current_section_content)
            if len(content) > 50:
                sections.append((current_section_title, content, page_num))
        
        # If no clear sections found, create sections from substantial paragraphs
        if not sections:
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 100:
                    # Try to extract a title from the first line
                    lines = paragraph.split('\n')
                    title = lines[0] if len(lines[0]) < 100 else f"Section {i+1}"
                    content = paragraph
                    sections.append((title, content, page_num))
        
        return sections
    
    def is_section_heading(self, line: str) -> bool:
        """Determine if a line is likely a section heading"""
        line = line.strip()
        
        # Skip very short or very long lines
        if len(line) < 5 or len(line) > 150:
            return False
        
        # Skip lines that end with periods (likely paragraph text)
        if line.endswith('.'):
            return False
        
        # Check for heading patterns
        patterns = [
            r'^(Chapter|CHAPTER)\s+\d+',
            r'^\d+\.',
            r'^\d+\.\d+',
            r'^[A-Z][A-Z\s]{5,}$',  # ALL CAPS
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$',  # Title Case
            r'^(Introduction|Conclusion|Abstract|Summary|Overview)',
            r'^\w+:$',  # Single word followed by colon
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        # Check if line is mostly uppercase and doesn't contain lowercase sentences
        if (line.isupper() and len(line) > 10 and 
            not re.search(r'[a-z]{3,}', line)):
            return True
        
        # Check for title case with reasonable length
        if (line.istitle() and 5 <= len(line.split()) <= 10):
            return True
        
        return False
    
    def calculate_relevance_score(self, section_title: str, section_content: str, 
                                persona: str, job_description: str) -> float:
        """Calculate relevance score for a section based on persona and job"""
        
        # Combine persona and job for keyword extraction
        query_text = f"{persona} {job_description}".lower()
        section_text = f"{section_title} {section_content}".lower()
        
        # Extract keywords from query
        query_keywords = self.extract_keywords(query_text)
        section_keywords = self.extract_keywords(section_text)
        
        # Calculate keyword overlap score
        overlap_score = len(query_keywords.intersection(section_keywords)) / max(len(query_keywords), 1)
        
        # Calculate TF-IDF-like score
        tfidf_score = self.calculate_tfidf_score(query_keywords, section_text)
        
        # Boost score for specific persona-job combinations
        boost_score = self.calculate_context_boost(section_title, section_content, persona, job_description)
        
        # Length penalty for very short sections
        length_penalty = min(len(section_content) / 200, 1.0)
        
        # Final score
        final_score = (overlap_score * 0.4 + tfidf_score * 0.3 + boost_score * 0.3) * length_penalty
        
        return final_score
    
    def extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text"""
        # Simple tokenization and cleaning
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Remove stop words and short words
        keywords = {word for word in words 
                   if word not in self.stop_words and len(word) > 3}
        
        return keywords
    
    def calculate_tfidf_score(self, query_keywords: set, section_text: str) -> float:
        """Calculate a simplified TF-IDF score"""
        if not query_keywords:
            return 0.0
        
        section_words = section_text.lower().split()
        total_words = len(section_words)
        
        if total_words == 0:
            return 0.0
        
        score = 0.0
        for keyword in query_keywords:
            # Term frequency
            tf = section_words.count(keyword) / total_words
            
            # Simple inverse document frequency approximation
            idf = math.log(1 + 1 / max(section_words.count(keyword), 1))
            
            score += tf * idf
        
        return score / len(query_keywords)
    
    def calculate_context_boost(self, section_title: str, section_content: str, 
                              persona: str, job_description: str) -> float:
        """Calculate context-specific boost based on persona and job"""
        boost = 0.0
        
        title_lower = section_title.lower()
        content_lower = section_content.lower()
        persona_lower = persona.lower()
        job_lower = job_description.lower()
        
        # Persona-specific boosts
        if 'travel' in persona_lower:
            travel_terms = [
                'itinerary', 'accommodation', 'transport', 'activities', 'attractions',
                'restaurant', 'hotel', 'sightseeing', 'tour', 'guide', 'tips'
            ]
            boost += sum(0.1 for term in travel_terms if term in title_lower or term in content_lower)
        
        if 'student' in persona_lower:
            study_terms = [
                'study', 'learn', 'concept', 'theory', 'practice', 'exam', 'test',
                'understand', 'explain', 'definition', 'example'
            ]
            boost += sum(0.1 for term in study_terms if term in title_lower or term in content_lower)
        
        if 'analyst' in persona_lower or 'business' in persona_lower:
            business_terms = [
                'revenue', 'profit', 'growth', 'market', 'strategy', 'analysis',
                'trend', 'performance', 'financial', 'investment'
            ]
            boost += sum(0.1 for term in business_terms if term in title_lower or term in content_lower)
        
        if 'hr' in persona_lower or 'human resource' in persona_lower:
            hr_terms = [
                'form', 'employee', 'onboarding', 'compliance', 'policy',
                'process', 'document', 'template', 'workflow'
            ]
            boost += sum(0.1 for term in hr_terms if term in title_lower or term in content_lower)
        
        if 'food' in persona_lower or 'chef' in persona_lower or 'contractor' in persona_lower:
            food_terms = [
                'recipe', 'ingredient', 'cooking', 'preparation', 'menu',
                'dish', 'meal', 'vegetarian', 'cuisine', 'buffet'
            ]
            boost += sum(0.1 for term in food_terms if term in title_lower or term in content_lower)
        
        # Job-specific boosts
        job_keywords = self.extract_keywords(job_lower)
        for keyword in job_keywords:
            if keyword in title_lower:
                boost += 0.2
            if keyword in content_lower:
                boost += 0.1
        
        return min(boost, 1.0)  # Cap the boost at 1.0
    
    def analyze_documents(self, input_data: Dict) -> Dict:
        """Analyze documents based on persona and job requirements"""
        
        documents = input_data.get('documents', [])
        persona = input_data.get('persona', {}).get('role', '')
        job_description = input_data.get('job_to_be_done', {}).get('task', '')
        
        all_sections = []
        
        # Process each document
        for doc_info in documents:
            filename = doc_info['filename']
            pdf_path = Path("/app/input") / filename
            
            if not pdf_path.exists():
                print(f"Warning: {filename} not found")
                continue
            
            print(f"Processing {filename}...")
            
            # Extract text from PDF
            pages_text = self.extract_text_from_pdf(str(pdf_path))
            
            # Extract sections from each page
            for page_num, text in pages_text.items():
                sections = self.extract_sections_from_text(text, page_num)
                
                for section_title, section_content, page in sections:
                    # Calculate relevance score
                    relevance_score = self.calculate_relevance_score(
                        section_title, section_content, persona, job_description
                    )
                    
                    all_sections.append({
                        'document': filename,
                        'section_title': section_title,
                        'content': section_content,
                        'page_number': page,
                        'relevance_score': relevance_score
                    })
        
        # Sort by relevance score (descending)
        all_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Select top sections for extracted_sections (top 10)
        extracted_sections = []
        for i, section in enumerate(all_sections[:10]):
            extracted_sections.append({
                'document': section['document'],
                'section_title': section['section_title'],
                'importance_rank': i + 1,
                'page_number': section['page_number']
            })
        
        # Select top sections for subsection_analysis (top 5 with content)
        subsection_analysis = []
        for section in all_sections[:5]:
            # Refine the content (truncate if too long)
            refined_text = section['content'][:1000] + "..." if len(section['content']) > 1000 else section['content']
            
            subsection_analysis.append({
                'document': section['document'],
                'refined_text': refined_text,
                'page_number': section['page_number']
            })
        
        # Build result
        result = {
            'metadata': {
                'input_documents': [doc['filename'] for doc in documents],
                'persona': persona,
                'job_to_be_done': job_description,
                'processing_timestamp': datetime.now().isoformat()
            },
            'extracted_sections': extracted_sections,
            'subsection_analysis': subsection_analysis
        }
        
        return result


def process_challenge1b():
    """Process Challenge 1B input"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find input JSON file
    input_files = list(input_dir.glob("challenge1b_input.json"))
    
    if not input_files:
        print("No challenge1b_input.json found in input directory")
        return
    
    input_file = input_files[0]
    print(f"Processing {input_file.name}...")
    
    # Load input data
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Initialize analyzer
    analyzer = PersonaDocumentAnalyzer()
    
    # Analyze documents
    result = analyzer.analyze_documents(input_data)
    
    # Save result
    output_file = output_dir / "challenge1b_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Completed analysis -> {output_file.name}")


if __name__ == "__main__":
    print("Starting persona-driven document analysis...")
    process_challenge1b()
    print("Document analysis completed!")