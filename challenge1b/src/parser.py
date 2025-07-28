"""
CLI Parser - Challenge 1B (Task Section Extractor)

Command-line interface for Round 1B (Task Section Extractor).
Optimized for Adobe Hack competition constraints.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

from .persona_extractor import PersonaTaskSectionExtractor
from .utils import validate_pdf_file, get_file_info, setup_logging


class PDFProcessor:
    """
    Main processor for PDF task section extraction (Round 1B).
    """
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the PDF processor."""
        self.logger = setup_logging(log_level)
        self.persona_extractor = PersonaTaskSectionExtractor(log_level)
    
    def process_task_sections(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Process PDF for task section extraction (Round 1B).
        
        Args:
            input_path (str): Path to input PDF
            output_path (str): Path to output JSON
            
        Returns:
            Dict[str, Any]: Processing results with timing and status
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not validate_pdf_file(input_path):
                return {
                    'success': False,
                    'error': f'Invalid PDF file: {input_path}',
                    'execution_time': 0
                }
            
            # Extract task sections
            self.logger.info(f"Starting task section extraction for {input_path}")
            persona_data = self.persona_extractor.extract_task_relevant_sections(input_path)
            
            # Save results
            success = self.persona_extractor.save_task_sections(persona_data, output_path)
            
            execution_time = time.time() - start_time
            
            result = {
                'success': success,
                'input_file': input_path,
                'output_file': output_path,
                'execution_time': round(execution_time, 2),
                'sections_found': len(persona_data.get('task_sections', []))
            }
            
            if success:
                self.logger.info(f"Task section extraction completed in {execution_time:.2f}s")
                
                # Add summary statistics
                sections = persona_data.get('task_sections', [])
                result['summary'] = {
                    'total_sections': len(sections),
                    'task_types': len(set(task for section in sections for task in section.get('relevant_tasks', []))),
                    'avg_relevance': round(sum(max(section.get('relevance_scores', {}).values()) for section in sections) / len(sections), 3) if sections else 0,
                    'section_types': list(set(section.get('section_type', 'unknown') for section in sections))
                }
            else:
                result['error'] = 'Failed to save task section data'
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error processing task sections: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'execution_time': round(execution_time, 2)
            }
    
    def batch_process(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        Batch process multiple PDF files.
        
        Args:
            input_dir (str): Directory containing PDF files
            output_dir (str): Directory for output files
            
        Returns:
            Dict[str, Any]: Batch processing results
        """
        from .utils import find_pdf_files
        
        pdf_files = find_pdf_files(input_dir)
        
        if not pdf_files:
            return {
                'success': False,
                'error': f'No PDF files found in {input_dir}',
                'processed_files': []
            }
        
        results = {
            'success': True,
            'total_files': len(pdf_files),
            'successful': 0,
            'failed': 0,
            'processed_files': [],
            'total_time': 0
        }
        
        start_time = time.time()
        
        for pdf_file in pdf_files:
            file_start = time.time()
            pdf_name = Path(pdf_file).stem
            
            try:
                task_output = Path(output_dir) / f"{pdf_name}_task_sections.json"
                task_result = self.process_task_sections(pdf_file, str(task_output))
                
                file_time = time.time() - file_start
                
                if task_result['success']:
                    results['successful'] += 1
                    status = 'success'
                else:
                    results['failed'] += 1
                    status = 'failed'
                
                results['processed_files'].append({
                    'file': pdf_file,
                    'status': status,
                    'execution_time': round(file_time, 2),
                    'task_result': task_result
                })
                
            except Exception as e:
                results['failed'] += 1
                results['processed_files'].append({
                    'file': pdf_file,
                    'status': 'error',
                    'error': str(e),
                    'execution_time': round(time.time() - file_start, 2)
                })
        
        results['total_time'] = round(time.time() - start_time, 2)
        results['success'] = results['failed'] == 0
        
        return results


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='PDF Task Section Extractor - Adobe Hack Challenge 1B',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract task sections from single PDF
  python parser.py persona input.pdf output_task_sections.json
  
  # Batch process directory
  python parser.py batch input_dir/ output_dir/
  
  # Docker usage
  docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \\
    --network none challenge1b python parser.py persona /app/input/doc.pdf /app/output/task_sections.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Processing mode')
    
    # Task section extraction
    persona_parser = subparsers.add_parser('persona', help='Extract task sections')
    persona_parser.add_argument('input', help='Input PDF file')
    persona_parser.add_argument('output', help='Output JSON file')
    
    # Batch processing
    batch_parser = subparsers.add_parser('batch', help='Batch process directory')
    batch_parser.add_argument('input_dir', help='Input directory containing PDF files')
    batch_parser.add_argument('output_dir', help='Output directory for JSON files')
    
    # Global options
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level (default: INFO)')
    parser.add_argument('--quiet', action='store_true', help='Suppress output except errors')
    parser.add_argument('--json-output', action='store_true', help='Output results as JSON')
    
    return parser


def print_results(results: Dict[str, Any], quiet: bool = False, json_output: bool = False):
    """Print processing results."""
    if json_output:
        print(json.dumps(results, indent=2))
        return
    
    if quiet and results.get('success'):
        return
    
    if 'processed_files' in results:
        # Batch processing results
        print(f"Batch processing completed in {results['total_time']}s")
        print(f"Files processed: {results['total_files']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        
        if not quiet:
            for file_result in results['processed_files']:
                status_symbol = "✓" if file_result['status'] == 'success' else "✗"
                print(f"  {status_symbol} {Path(file_result['file']).name} "
                      f"({file_result['execution_time']}s)")
    
    else:
        # Single processing result
        status = "✓" if results['success'] else "✗"
        print(f"{status} Processing completed in {results['execution_time']}s")
        
        if 'sections_found' in results:
            print(f"  - Found {results['sections_found']} task sections")
            
        if 'summary' in results:
            summary = results['summary']
            print(f"  - Task types: {summary['task_types']}")
            print(f"  - Average relevance: {summary['avg_relevance']}")
            print(f"  - Section types: {', '.join(summary['section_types'])}")
    
    if not results['success'] and 'error' in results:
        print(f"Error: {results['error']}", file=sys.stderr)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize processor
    processor = PDFProcessor(args.log_level)
    
    try:
        # Execute command
        if args.command == 'persona':
            results = processor.process_task_sections(args.input, args.output)
        
        elif args.command == 'batch':
            results = processor.batch_process(args.input_dir, args.output_dir)
        
        # Print results
        print_results(results, args.quiet, args.json_output)
        
        # Exit with appropriate code
        sys.exit(0 if results['success'] else 1)
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user", file=sys.stderr)
        sys.exit(130)
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()