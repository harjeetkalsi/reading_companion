# Python slim for smaller image
FROM python:3.11-slim

# Make apt non-interactive and pip quieter
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# System deps (CA certs fix + curl; add a few common headless libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl build-essential \
    libglib2.0-0 libnss3 libgdk-pixbuf-2.0-0 libgtk-3-0 libx11-6 \
    libxcb1 libxcomposite1 libxrandr2 libxi6 libxrender1 libxext6 \
    libxcursor1 libxdamage1 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Layer caching: install deps first
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Streamlit config
ENV PYTHONPATH=/app \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXsrfProtection=false \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

# Correct Streamlit health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

# Run the app
CMD ["streamlit", "run", "reading_companion/app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
