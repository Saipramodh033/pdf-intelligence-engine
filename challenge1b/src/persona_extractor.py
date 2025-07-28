"""
Round 1B - Document Section Extractor for Persona Tasks

Extracts document sections relevant to persona tasks rather than extracting personas from documents.
Optimized for competition constraints: CPU-only, <200MB, offline, <10s execution.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter

import fitz  # PyMuPDF
import numpy as np
try:
    from langdetect import detect, LangDetectError
except ImportError:
    # Fallback if langdetect is not available
    def detect(text):
        return 'en'
    class LangDetectError(Exception):
        pass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class PersonaTaskSectionExtractor:
    """
    Extract document sections relevant to persona tasks from PDF using NLP and pattern matching.
    Designed for Adobe Hack Round 1B requirements.
    """
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the section extractor."""
        self.logger = self._setup_logger(log_level)
        
        # Define persona tasks and their characteristics
        self.persona_tasks = {
            'data_analysis': {
                'keywords': ['analyze', 'analysis', 'data', 'statistics', 'metrics', 'insights', 'trends', 'patterns'],
                'patterns': [
                    r'(?:data|statistical|quantitative)\s+(?:analysis|examination|study)',
                    r'(?:analyze|examine|investigate)\s+(?:data|results|findings)',
                    r'(?:metrics|kpis?|indicators)\s+(?:show|indicate|reveal)',
                    r'(?:trends|patterns|correlations)\s+(?:in|within|across)',
                ]
            },
            'system_design': {
                'keywords': ['architecture', 'design', 'system', 'framework', 'structure', 'components', 'modules'],
                'patterns': [
                    r'(?:system|software|application)\s+(?:architecture|design|structure)',
                    r'(?:components?|modules?|services?)\s+(?:interact|communicate|integrate)',
                    r'(?:framework|platform|infrastructure)\s+(?:supports?|enables?|provides?)',
                    r'(?:scalable|modular|distributed)\s+(?:design|architecture|system)',
                ]
            },
            'implementation': {
                'keywords': ['implement', 'develop', 'build', 'create', 'code', 'programming', 'deployment'],
                'patterns': [
                    r'(?:implement|develop|build|create)\s+(?:solution|system|application|feature)',
                    r'(?:code|programming|development)\s+(?:standards|practices|guidelines)',
                    r'(?:deployment|installation|setup)\s+(?:process|procedure|steps)',
                    r'(?:testing|validation|verification)\s+(?:approach|strategy|methods)',
                ]
            },
            'troubleshooting': {
                'keywords': ['debug', 'troubleshoot', 'error', 'issue', 'problem', 'fix', 'resolve', 'solution'],
                'patterns': [
                    r'(?:debug|troubleshoot|diagnose)\s+(?:issues?|problems?|errors?)',
                    r'(?:common|typical|frequent)\s+(?:issues?|problems?|errors?)',
                    r'(?:error|exception|failure)\s+(?:handling|management|recovery)',
                    r'(?:fix|resolve|solve|address)\s+(?:problems?|issues?|bugs?)',
                ]
            },
            'optimization': {
                'keywords': ['optimize', 'performance', 'efficiency', 'improve', 'enhance', 'tuning'],
                'patterns': [
                    r'(?:optimize|improve|enhance)\s+(?:performance|efficiency|speed)',
                    r'(?:performance|efficiency)\s+(?:tuning|optimization|improvement)',
                    r'(?:bottlenecks?|constraints?|limitations?)\s+(?:identified?|addressed?)',
                    r'(?:scalability|throughput|latency)\s+(?:considerations?|requirements?)',
                ]
            },
            'documentation': {
                'keywords': ['document', 'documentation', 'guide', 'manual', 'instructions', 'procedures'],
                'patterns': [
                    r'(?:documentation|guide|manual)\s+(?:provides?|describes?|explains?)',
                    r'(?:instructions?|procedures?|steps?)\s+(?:for|to)\s+(?:follow|complete)',
                    r'(?:reference|specification|standard)\s+(?:document|guide|manual)',
                    r'(?:user|technical|api)\s+(?:documentation|guide|reference)',
                ]
            },
            'planning': {
                'keywords': ['plan', 'strategy', 'roadmap', 'timeline', 'schedule', 'requirements', 'objectives'],
                'patterns': [
                    r'(?:plan|strategy|roadmap)\s+(?:for|to)\s+(?:implement|achieve|deliver)',
                    r'(?:requirements?|objectives?|goals?)\s+(?:defined?|specified?|outlined?)',
                    r'(?:timeline|schedule|milestones?)\s+(?:for|of)\s+(?:project|development)',
                    r'(?:phases?|stages?|iterations?)\s+(?:of|in)\s+(?:development|implementation)',
                ]
            },
            'collaboration': {
                'keywords': ['collaborate', 'team', 'communication', 'coordination', 'stakeholder', 'meeting'],
                'patterns': [
                    r'(?:collaborate|coordinate|communicate)\s+(?:with|between)\s+(?:teams?|stakeholders?)',
                    r'(?:meetings?|discussions?|reviews?)\s+(?:with|between|among)',
                    r'(?:stakeholder|client|customer)\s+(?:engagement|communication|feedback)',
                    r'(?:cross-functional|interdisciplinary)\s+(?:collaboration|coordination)',
                ]
            }
        }
        
        # Section type patterns for better categorization
        self.section_type_patterns = {
            'methodology': [
                r'(?:methodology|approach|method|technique|procedure)',
                r'(?:step-by-step|process|workflow|pipeline)',
            ],
            'requirements': [
                r'(?:requirements?|specifications?|criteria|constraints?)',
                r'(?:must|should|shall|required|mandatory|optional)',
            ],
            'examples': [
                r'(?:example|sample|illustration|case study|demonstration)',
                r'(?:for instance|for example|such as|including)',
            ],
            'best_practices': [
                r'(?:best practices?|recommendations?|guidelines?|standards?)',
                r'(?:recommended|suggested|preferred|optimal)',
            ],
            'tools_resources': [
                r'(?:tools?|resources?|utilities|libraries|frameworks?)',
                r'(?:using|with|via|through|leveraging)',
            ]
        }
        
        # Initialize lightweight classifier for section classification
        self._init_classifier()
    
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
    
    def _init_classifier(self):
        """Initialize lightweight ML classifier for section classification."""
        # Simple pipeline with TF-IDF and Naive Bayes (very lightweight)
        self.text_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Pre-trained on synthetic data for task relevance classification
        self._train_classifier()
    
    def _train_classifier(self):
        """Train classifier with synthetic examples for task relevance."""
        # Synthetic training data for different persona tasks
        training_texts = [
            # Data analysis
            "analyze customer behavior patterns", "statistical analysis of results", "data visualization techniques",
            "metrics show significant improvement", "correlation between variables", "trend analysis over time",
            
            # System design
            "system architecture overview", "component interaction diagram", "scalable design patterns",
            "modular framework structure", "distributed system design", "microservices architecture",
            
            # Implementation
            "implementation guidelines", "coding standards and practices", "deployment procedures",
            "development workflow", "testing methodology", "continuous integration setup",
            
            # Troubleshooting
            "common error messages", "debugging techniques", "troubleshooting guide",
            "error handling strategies", "problem resolution steps", "diagnostic procedures",
            
            # Optimization
            "performance optimization", "efficiency improvements", "bottleneck identification",
            "scalability considerations", "resource utilization", "speed enhancements",
            
            # Documentation
            "user guide instructions", "technical documentation", "API reference manual",
            "installation procedures", "configuration settings", "usage examples",
            
            # Planning
            "project roadmap", "development timeline", "requirements specification",
            "milestone planning", "resource allocation", "strategic objectives",
            
            # Collaboration
            "team coordination", "stakeholder communication", "meeting protocols",
            "cross-functional collaboration", "feedback collection", "review processes",
        ]
        
        training_labels = [
            'data_analysis', 'data_analysis', 'data_analysis', 'data_analysis', 'data_analysis', 'data_analysis',
            'system_design', 'system_design', 'system_design', 'system_design', 'system_design', 'system_design',
            'implementation', 'implementation', 'implementation', 'implementation', 'implementation', 'implementation',
            'troubleshooting', 'troubleshooting', 'troubleshooting', 'troubleshooting', 'troubleshooting', 'troubleshooting',
            'optimization', 'optimization', 'optimization', 'optimization', 'optimization', 'optimization',
            'documentation', 'documentation', 'documentation', 'documentation', 'documentation', 'documentation',
            'planning', 'planning', 'planning', 'planning', 'planning', 'planning',
            'collaboration', 'collaboration', 'collaboration', 'collaboration', 'collaboration', 'collaboration',
        ]
        
        try:
            self.text_classifier.fit(training_texts, training_labels)
        except Exception as e:
            self.logger.warning(f"Failed to train classifier: {e}")
    
    def extract_task_relevant_sections(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract document sections relevant to persona tasks from PDF file.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Dict[str, Any]: Structured sections in competition format
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Extract text with context
            text_data = self._extract_text_with_context(doc)
            
            # Detect language
            language = self._detect_language(text_data)
            
            # Extract sections relevant to persona tasks
            task_sections = self._extract_task_sections(text_data, language)
            
            doc.close()
            
            result = {
                "task_sections": task_sections
            }
            
            self.logger.info(f"Extracted {len(task_sections)} task-relevant sections from {pdf_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting task sections from {pdf_path}: {str(e)}")
            return {"task_sections": []}
    
    def _extract_text_with_context(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Extract text with paragraph-level context."""
        text_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Split into paragraphs (better for section extraction)
            paragraphs = re.split(r'\n\s*\n', text)
            
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if len(paragraph) < 20:  # Skip very short paragraphs
                    continue
                
                # Get context (previous and next paragraphs)
                context_before = paragraphs[i-1] if i > 0 else ""
                context_after = paragraphs[i+1] if i < len(paragraphs)-1 else ""
                
                text_data.append({
                    'text': paragraph,
                    'page': page_num + 1,
                    'context_before': context_before.strip(),
                    'context_after': context_after.strip(),
                    'full_context': f"{context_before} {paragraph} {context_after}".strip()
                })
        
        return text_data
    
    def _detect_language(self, text_data: List[Dict[str, Any]]) -> str:
        """Detect document language."""
        sample_text = " ".join([item['text'] for item in text_data[:50]])
        
        # Check for Japanese characters
        japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', sample_text))
        
        if japanese_chars > 20:
            return 'japanese'
        
        try:
            detected = detect(sample_text)
            return 'japanese' if detected == 'ja' else 'english'
        except LangDetectError:
            return 'english'
    
    def _extract_task_sections(self, text_data: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Extract sections relevant to persona tasks using pattern matching and ML."""
        task_sections = []
        
        for item in text_data:
            text = item['text']
            full_context = item['full_context']
            
            # Score this section for each persona task
            task_scores = self._score_section_for_tasks(text, full_context)
            
            # Find the best matching task(s) above threshold
            relevant_tasks = [(task, score) for task, score in task_scores.items() if score > 0.3]
            
            if relevant_tasks:
                # Sort by score and take top tasks
                relevant_tasks.sort(key=lambda x: x[1], reverse=True)
                
                # Determine section type
                section_type = self._classify_section_type(text)
                
                # Create section entry
                section = {
                    'text': text,
                    'page': item['page'],
                    'relevant_tasks': [task for task, score in relevant_tasks[:3]],  # Top 3 tasks
                    'relevance_scores': {task: round(score, 3) for task, score in relevant_tasks[:3]},
                    'section_type': section_type,
                    'length': len(text),
                    'context_available': bool(item['context_before'] or item['context_after'])
                }
                
                task_sections.append(section)
        
        # Sort by relevance and remove duplicates
        task_sections = self._deduplicate_sections(task_sections)
        
        return task_sections
    
    def _score_section_for_tasks(self, text: str, context: str) -> Dict[str, float]:
        """Score a text section for relevance to each persona task."""
        scores = {}
        text_lower = text.lower()
        context_lower = context.lower()
        
        for task_name, task_info in self.persona_tasks.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in task_info['keywords'] 
                                if keyword in text_lower)
            score += keyword_matches * 0.1
            
            # Pattern matching
            pattern_matches = 0
            for pattern in task_info['patterns']:
                if re.search(pattern, text_lower):
                    pattern_matches += 1
            score += pattern_matches * 0.3
            
            # Context relevance (if available)
            if context_lower:
                context_keyword_matches = sum(1 for keyword in task_info['keywords'] 
                                            if keyword in context_lower)
                score += context_keyword_matches * 0.05
            
            # ML classifier prediction (if available)
            try:
                prediction = self.text_classifier.predict([text])[0]
                if prediction == task_name:
                    score += 0.4
            except Exception:
                pass
            
            scores[task_name] = min(score, 1.0)  # Cap at 1.0
        
        return scores
    
    def _classify_section_type(self, text: str) -> str:
        """Classify the type of section based on content patterns."""
        text_lower = text.lower()
        
        for section_type, patterns in self.section_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return section_type
        
        # Default classification based on content characteristics
        if len(text) > 500:
            return 'detailed_explanation'
        elif any(word in text_lower for word in ['step', 'first', 'then', 'next', 'finally']):
            return 'procedure'
        elif any(word in text_lower for word in ['example', 'instance', 'case']):
            return 'examples'
        else:
            return 'general_content'
    
    def _deduplicate_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar sections."""
        unique_sections = []
        seen_texts = set()
        
        # Sort by highest relevance score first
        sections.sort(key=lambda x: max(x['relevance_scores'].values()), reverse=True)
        
        for section in sections:
            text_key = section['text'][:100].lower().strip()  # Use first 100 chars as key
            
            # Check for similarity with existing sections
            is_duplicate = False
            for seen_text in seen_texts:
                if self._text_similarity(text_key, seen_text) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_texts.add(text_key)
                unique_sections.append(section)
        
        return unique_sections[:20]  # Limit to top 20 sections
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def save_task_sections(self, section_data: Dict[str, Any], output_path: str) -> bool:
        """Save task sections to JSON file."""
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(section_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Task sections saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving task sections to {output_path}: {str(e)}")
            return False
    
    def process_pdf(self, input_path: str, output_path: str) -> bool:
        """Process PDF and save task sections (main entry point)."""
        section_data = self.extract_task_relevant_sections(input_path)
        return self.save_task_sections(section_data, output_path)


def main():
    """CLI entry point for testing."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python persona_extractor.py <input_pdf> <output_json>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    extractor = PersonaTaskSectionExtractor()
    success = extractor.process_pdf(input_path, output_path)
    
    if success:
        print(f"Task sections extracted successfully: {output_path}")
    else:
        print("Failed to extract task sections")
        sys.exit(1)


if __name__ == "__main__":
    main()