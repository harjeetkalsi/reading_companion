# -------- Dockerfile (place it at coding_projects/reading_companion/Dockerfile OR just reuse this path below with -f) --------
FROM python:3.11-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# System packages (kept minimal; you can drop GUI libs if not using Selenium/Chromium)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     build-essential curl ca-certificates \
     libglib2.0-0 libnss3 libgdk-pixbuf-2.0-0 libgtk-3-0 libx11-6 \
     libxcb1 libxcomposite1 libxrandr2 libxi6 libxrender1 libxext6 \
     libxcursor1 libxdamage1 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Put the project under /opt/workspace/reading_companion
WORKDIR /opt/workspace

# 1) Install Python deps first (better layer cache)
COPY reading_companion/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy the whole package directory
COPY reading_companion /opt/workspace/reading_companion

# Make "import reading_companion" work (parent of the package on PYTHONPATH)
ENV PYTHONPATH=/opt/workspace

# Quick sanity check: fail build if the app entrypoint isn't where we expect
RUN test -f /opt/workspace/reading_companion/app/app.py

# Streamlit settings
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

# Run the app the same way you do locally (from parent of the package)
CMD ["python", "-m", "streamlit", "run", "reading_companion/app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
