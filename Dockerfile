# Base
FROM python:3.11-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# System deps (headless-friendly & certs)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     build-essential curl ca-certificates \
     libglib2.0-0 libnss3 libgdk-pixbuf-2.0-0 libgtk-3-0 libx11-6 \
     libxcb1 libxcomposite1 libxrandr2 libxi6 libxrender1 libxext6 \
     libxcursor1 libxdamage1 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Workdir for the image
WORKDIR /opt/app

# Install deps first (layer-cached)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire repo -> /opt/app/reading_companion
# (so /opt/app/reading_companion/app/app.py exists)
COPY . /opt/app/reading_companion

# Make 'reading_companion' importable
ENV PYTHONPATH=/opt/app

# Streamlit settings
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

# Run exactly like you do locally (module path)
CMD ["python", "-m", "streamlit", "run", "reading_companion/app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
