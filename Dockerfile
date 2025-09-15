# Base
FROM python:3.11-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# System deps (for headless Chromium/Selenium friendliness & certs)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     build-essential curl ca-certificates \
     libglib2.0-0 libnss3 libgdk-pixbuf-2.0-0 libgtk-3-0 libx11-6 \
     libxcb1 libxcomposite1 libxrandr2 libxi6 libxrender1 libxext6 \
     libxcursor1 libxdamage1 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Project root inside the container
WORKDIR /opt/app

# Layer-cached deps first
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire repo into /opt/app (so /opt/app/reading_companion/... exists)
COPY . .

# Make imports like `from reading_companion.core...` work
ENV PYTHONPATH=/opt/app

# Streamlit config
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

# Run exactly like you do locally (module path relative to repo root)
CMD ["python", "-m", "streamlit", "run", "reading_companion/app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
