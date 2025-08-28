# Python slim for smaller image
FROM python:3.11-slim

# System deps (for building some libs)
RUN apt-get update && apt-get install -y \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . /app

# Streamlit tweaks
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXsrfProtection=false
ENV STREAMLIT_SERVER_PORT=8501

# Expose port
EXPOSE 8501

# Healthcheck (optional)
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the app
CMD ["streamlit", "run", "reading_companion/app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
