# Adobe Hack Competition - Challenge 1A (Outline Extractor)
# Optimized for: CPU-only, <200MB, offline, <10s execution

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables for optimization
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Install minimal system dependencies including MuPDF libraries for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libgl1 \
    libmupdf-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libopenjp2-7-dev \
    libjbig-dev \
    libharfbuzz-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && \
    rm -rf /tmp/* /var/tmp/* ~/.cache/pip

# Copy application code
COPY src/ ./src/

# Create input and output directories with proper permissions
RUN mkdir -p input output && \
    chmod 755 input output

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check - verify the application can start
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=2 \
    CMD python -c "from src.outline_extractor import OutlineExtractor; print('OK')" || exit 1

# Default command - CLI parser
CMD ["python", "-m", "src.parser", "--help"]

# Competition-specific labels
LABEL maintainer="Adobe Hack Team"
LABEL description="PDF Outline Extractor - Challenge 1A"
LABEL version="1.0.0"
LABEL competition="Adobe Hack 2024"
LABEL constraints="CPU-only, <200MB, offline, <10s execution"

# Expose volumes for input/output (competition requirement)
VOLUME ["/app/input", "/app/output"]

# Competition usage examples in labels
LABEL usage.outline="docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none challenge1a python -m src.parser outline /app/input/doc.pdf /app/output/outline.json"
LABEL usage.batch="docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none challenge1a python -m src.parser batch /app/input /app/output"

# Build optimization - remove unnecessary files
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Final image size optimization
RUN du -sh /app && \
    echo "Challenge 1A image build completed - optimized for competition constraints"