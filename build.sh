#!/bin/bash

# Adobe Hack Competition - Build and Test Script
# Builds Docker image and runs validation tests

set -e  # Exit on any error

echo "🏆 Adobe Hack Competition - Build Script"
echo "========================================"
echo "Building PDF Outline & Persona Extractor"
echo "Round 1A & 1B Solution"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
check_docker() {
    print_status "Checking Docker availability..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    print_success "Docker is available"
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    mkdir -p input output
    print_success "Directories created"
}

# Run local validation tests
run_validation() {
    print_status "Running validation tests..."
    
    if [ -f "test_validation.py" ]; then
        python3 test_validation.py
        if [ $? -eq 0 ]; then
            print_success "Validation tests passed"
        else
            print_error "Validation tests failed"
            exit 1
        fi
    else
        print_warning "Validation script not found, skipping tests"
    fi
}

# Build Docker image
build_docker() {
    print_status "Building Docker image..."
    
    # Build with optimization flags
    docker build \
        --tag outline-extractor:latest \
        --tag outline-extractor:competition \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
        
        # Show image size
        IMAGE_SIZE=$(docker images outline-extractor:latest --format "{{.Size}}")
        print_status "Image size: $IMAGE_SIZE"
        
        # Check if under 200MB constraint
        SIZE_MB=$(docker images outline-extractor:latest --format "{{.Size}}" | sed 's/MB//' | sed 's/GB/000/' | cut -d'.' -f1)
        if [ "$SIZE_MB" -lt 200 ] 2>/dev/null; then
            print_success "Image size is under 200MB constraint ✓"
        else
            print_warning "Image size may exceed 200MB constraint"
        fi
    else
        print_error "Docker build failed"
        exit 1
    fi
}

# Test Docker image
test_docker() {
    print_status "Testing Docker image..."
    
    # Test basic functionality
    print_status "Testing basic container startup..."
    docker run --rm outline-extractor:latest python -c "
from app.src.outline_extractor import OutlineExtractor
from app.src.persona_extractor import PersonaExtractor
print('✓ Modules imported successfully')
print('✓ Container is working')
"
    
    if [ $? -eq 0 ]; then
        print_success "Docker container test passed"
    else
        print_error "Docker container test failed"
        exit 1
    fi
    
    # Test CLI help
    print_status "Testing CLI interface..."
    docker run --rm outline-extractor:latest python -m app.src.parser --help > /dev/null
    
    if [ $? -eq 0 ]; then
        print_success "CLI interface test passed"
    else
        print_error "CLI interface test failed"
        exit 1
    fi
}

# Generate sample outputs
generate_samples() {
    print_status "Generating sample outputs..."
    
    # Run the validation script to generate samples
    python3 -c "
import sys
sys.path.insert(0, '.')
from test_validation import generate_sample_outputs
generate_sample_outputs()
"
    
    if [ $? -eq 0 ]; then
        print_success "Sample outputs generated"
        
        # List generated files
        if [ -d "output" ]; then
            print_status "Generated files:"
            ls -la output/
        fi
    else
        print_warning "Sample generation failed"
    fi
}

# Show usage examples
show_usage() {
    echo ""
    echo "🚀 Usage Examples"
    echo "================="
    echo ""
    echo "Local usage:"
    echo "  python -m app.src.parser outline input/doc.pdf output/outline.json"
    echo "  python -m app.src.parser persona input/doc.pdf output/personas.json"
    echo "  python -m app.src.parser both input/doc.pdf output/outline.json output/personas.json"
    echo ""
    echo "Docker usage (competition format):"
    echo "  # Round 1A - Outline extraction"
    echo "  docker run --rm \\"
    echo "    -v \$(pwd)/input:/app/input \\"
    echo "    -v \$(pwd)/output:/app/output \\"
    echo "    --network none \\"
    echo "    outline-extractor \\"
    echo "    python -m app.src.parser outline /app/input/doc.pdf /app/output/outline.json"
    echo ""
    echo "  # Round 1B - Persona extraction"
    echo "  docker run --rm \\"
    echo "    -v \$(pwd)/input:/app/input \\"
    echo "    -v \$(pwd)/output:/app/output \\"
    echo "    --network none \\"
    echo "    outline-extractor \\"
    echo "    python -m app.src.parser persona /app/input/doc.pdf /app/output/personas.json"
    echo ""
    echo "  # Both rounds"
    echo "  docker run --rm \\"
    echo "    -v \$(pwd)/input:/app/input \\"
    echo "    -v \$(pwd)/output:/app/output \\"
    echo "    --network none \\"
    echo "    outline-extractor \\"
    echo "    python -m app.src.parser both /app/input/doc.pdf /app/output/outline.json /app/output/personas.json"
    echo ""
}

# Main execution
main() {
    echo "Starting build process..."
    echo ""
    
    # Parse command line arguments
    BUILD_DOCKER=true
    RUN_TESTS=true
    GENERATE_SAMPLES=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-docker)
                BUILD_DOCKER=false
                shift
                ;;
            --no-tests)
                RUN_TESTS=false
                shift
                ;;
            --no-samples)
                GENERATE_SAMPLES=false
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --no-docker    Skip Docker build"
                echo "  --no-tests     Skip validation tests"
                echo "  --no-samples   Skip sample generation"
                echo "  --help         Show this help"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Setup
    setup_directories
    
    # Run validation tests
    if [ "$RUN_TESTS" = true ]; then
        run_validation
    fi
    
    # Build Docker image
    if [ "$BUILD_DOCKER" = true ]; then
        check_docker
        build_docker
        test_docker
    fi
    
    # Generate samples
    if [ "$GENERATE_SAMPLES" = true ]; then
        generate_samples
    fi
    
    # Show usage
    show_usage
    
    echo ""
    print_success "Build completed successfully! 🎉"
    print_status "Solution is ready for Adobe Hack competition submission"
    echo ""
}

# Run main function
main "$@"