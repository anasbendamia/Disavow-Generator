# Dockerfile
# Copyright (c) 2026 Banshee (https://www.banshee.pro)
# License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

FROM python:3.11-slim

LABEL org.opencontainers.image.title="Disavow Generator"
LABEL org.opencontainers.image.description="Negative SEO protection web app with automated, hierarchical and historical Google Search Console disavow generation and granular link-level control"
LABEL org.opencontainers.image.source="https://github.com/BansheeTech/Disavow-Generator"
LABEL org.opencontainers.image.licenses="AGPL-3.0"

WORKDIR /app

# Dpeps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gosu for dropping privileges
RUN apt-get update && apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/*

# App
COPY app.py .
COPY pymodules/ pymodules/
COPY ui/ ui/

# Usr
RUN useradd -m -u 1000 disavow && \
    mkdir -p __DISAVOW_DATA__/INGEST __DISAVOW_DATA__/OUTPUT conf && \
    chown -R disavow:disavow /app

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose
EXPOSE 44444

# Hehehahaok
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:44444/login')" || exit 1

# Glory
ENTRYPOINT ["/entrypoint.sh"]
